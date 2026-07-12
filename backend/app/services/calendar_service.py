import logging

from datetime import datetime, time

from sqlalchemy.orm import Session

from app.models.meeting import Meeting

from app.services.google_client import (
    build_google_service
)

from app.ai.task_extraction_agent import (
    extract_tasks_from_new_meetings
)

from app.enums.meeting_enum import (
    MeetingType,
    MeetingStatus
)

logger = logging.getLogger(__name__)

CALENDAR_SCOPE = [
    "https://www.googleapis.com/auth/calendar.readonly"
]


# =====================================================
# FETCH CALENDAR EVENTS
# =====================================================
from datetime import datetime, timedelta, timezone
def get_calendar_events(
    service,
    max_results: int = 100
):

    try:

        now = datetime.now(timezone.utc)

        time_min = now.isoformat()

        time_max = (

            now + timedelta(days=30)

        ).isoformat()

        response = (

            service.events()

            .list(

                calendarId="primary",

                timeMin=time_min,

                timeMax=time_max,

                singleEvents=True,

                orderBy="startTime",

                maxResults=max_results

            )

            .execute()

        )

        events = response.get(
            "items",
            []
        )

        logger.info(

            "Fetched %d upcoming calendar events.",

            len(events)

        )

        return events

    except Exception as e:

        logger.exception(e)

        raise


# =====================================================
# EXTRACT EVENT DATA
# =====================================================

def extract_meeting_data(
    user_id: int,
    event: dict
):

    start = event.get(
        "start",
        {}
    )

    end = event.get(
        "end",
        {}
    )

    start_value = start.get(
        "dateTime"
    ) or start.get(
        "date"
    )

    end_value = end.get(
        "dateTime"
    ) or end.get(
        "date"
    )

    # -------------------------------
    # Handle All-Day Events
    # -------------------------------

    if "T" in start_value:

        start_time = datetime.fromisoformat(
            start_value.replace(
                "Z",
                "+00:00"
            )
        )

        end_time = datetime.fromisoformat(
            end_value.replace(
                "Z",
                "+00:00"
            )
        )

    else:

        start_date = datetime.fromisoformat(
            start_value
        ).date()

        end_date = datetime.fromisoformat(
            end_value
        ).date()

        start_time = datetime.combine(
            start_date,
            time.min
        )

        end_time = datetime.combine(
            end_date,
            time.min
        )

    # -------------------------------
    # Attendees
    # -------------------------------

    attendee_list = []

    for attendee in event.get(
        "attendees",
        []
    ):

        attendee_list.append(

            attendee.get(
                "email",
                ""
            )

        )

    attendees = ",".join(
        attendee_list
    )

    # -------------------------------
    # Organizer
    # -------------------------------

    organizer = (

        event.get(
            "organizer",
            {}
        )

        .get(
            "email"
        )

    )

    # -------------------------------
    # Meeting Link
    # -------------------------------

    meeting_link = event.get(
        "hangoutLink"
    )

    # -------------------------------
    # Meeting Type
    # -------------------------------

    if meeting_link:

        meeting_type = (
            MeetingType.ONLINE
        )

    else:

        meeting_type = (
            MeetingType.OFFLINE
        )

    # -------------------------------
    # Status
    # -------------------------------

    status_string = (

        event.get(
            "status",
            "confirmed"
        )

        .upper()

    )

    try:

        meeting_status = MeetingStatus(
            status_string
        )

    except ValueError:

        meeting_status = (
            MeetingStatus.CONFIRMED
        )

    # -------------------------------
    # Return Meeting Dictionary
    # -------------------------------

    return {

        "user_id": user_id,

        "google_event_id": event.get(
            "id"
        ),

        "title": event.get(
            "summary",
            "Untitled Meeting"
        ),

        "description": event.get(
            "description"
        ),

        "organizer": organizer,

        "location": event.get(
            "location"
        ),

        "meeting_link": meeting_link,

        "attendees": attendees,

        "start_time": start_time,

        "end_time": end_time,

        "meeting_type": meeting_type,

        "status": meeting_status

    }

# =====================================================
# SAVE MEETING
# =====================================================

def save_meeting(
    db: Session,
    meeting_data: dict
):

    existing = (

        db.query(Meeting)

        .filter(
            Meeting.user_id == meeting_data["user_id"]
        )

        .filter(
            Meeting.google_event_id ==
            meeting_data["google_event_id"]
        )

        .first()

    )

    if existing:

        return None

    return Meeting(
        **meeting_data
    )

# =====================================================
# SYNC CALENDAR
# =====================================================

def sync_calendar(
    db: Session,
    user_id: int
):

    logger.info(
        "Starting Google Calendar Sync for user %s",
        user_id
    )

    service = build_google_service(

        db=db,

        user_id=user_id,

        api_name="calendar",

        version="v3",

        scopes=CALENDAR_SCOPE

    )

    events = get_calendar_events(
        service
    )

    meetings_to_insert = []

    synced = 0

    skipped = 0

    failed = 0

    for event in events:

        try:

            meeting_data = extract_meeting_data(

                user_id=user_id,

                event=event

            )

            meeting = save_meeting(

                db=db,

                meeting_data=meeting_data

            )

            if meeting:

                meetings_to_insert.append(
                    meeting
                )

                synced += 1

            else:

                skipped += 1

        except Exception as e:

            failed += 1

            logger.exception(

                "Failed to process event %s",

                event.get("id")

            )

    try:

        if meetings_to_insert:

            db.add_all(

                meetings_to_insert

            )

            db.commit()

            logger.info(

                "%d meetings inserted.",

                len(meetings_to_insert)

            )

            # See gmail_service.py for why this runs after commit and why
            # it can't take down the sync on failure.
            extract_tasks_from_new_meetings(
                db,
                meetings_to_insert
            )

    except Exception as e:

        db.rollback()

        logger.exception(e)

        raise

    logger.info(

        "Calendar Sync Finished."

    )

    logger.info(

        "Synced=%d Skipped=%d Failed=%d",

        synced,

        skipped,

        failed

    )

    return {

        "success": True,

        "synced": synced,

        "skipped": skipped,

        "failed": failed,

        "total": len(events)

    }


# =====================================================
# TODAY'S MEETINGS
# =====================================================

def get_today_calendar_meetings(
    db: Session,
    user_id: int
):

    today = datetime.now().date()

    return (

        db.query(Meeting)

        .filter(
            Meeting.user_id == user_id
        )

        .filter(
            Meeting.start_time >= datetime.combine(
                today,
                time.min
            )
        )

        .filter(
            Meeting.start_time <= datetime.combine(
                today,
                time.max
            )
        )

        .order_by(
            Meeting.start_time
        )

        .all()

    )


# =====================================================
# UPCOMING MEETINGS
# =====================================================

def get_upcoming_calendar_meetings(
    db: Session,
    user_id: int,
    limit: int = 10
):

    return (

        db.query(Meeting)

        .filter(
            Meeting.user_id == user_id
        )

        .filter(
            Meeting.start_time > datetime.now()
        )

        .order_by(
            Meeting.start_time
        )

        .limit(limit)

        .all()

    )