from datetime import datetime

from sqlalchemy.orm import Session

from app.models.meeting import Meeting

from app.analytics.meeting_analytics import (
    calculate_total_meeting_hours,
    detect_conflicts,
    calculate_free_slots,
    calculate_best_focus_window,
    calculate_meeting_load
)


# ==========================================================
# CRUD
# ==========================================================

def get_all_meetings(
    db: Session,
    user_id: int
):

    return (

        db.query(Meeting)

        .filter(
            Meeting.user_id == user_id
        )

        .order_by(
            Meeting.start_time
        )

        .all()

    )


def create_meeting(
    db: Session,
    meeting_data: dict
):

    meeting = Meeting(
        **meeting_data
    )

    db.add(meeting)

    db.commit()

    db.refresh(meeting)

    return meeting


def get_meeting_by_id(
    db: Session,
    user_id: int,
    meeting_id: int
):

    return (

        db.query(Meeting)

        .filter(
            Meeting.user_id == user_id
        )

        .filter(
            Meeting.id == meeting_id
        )

        .first()

    )


def get_meeting_by_google_event_id(
    db: Session,
    user_id: int,
    google_event_id: str
):

    return (

        db.query(Meeting)

        .filter(
            Meeting.user_id == user_id
        )

        .filter(
            Meeting.google_event_id == google_event_id
        )

        .first()

    )


# ==========================================================
# GOOGLE CALENDAR
# ==========================================================

def save_google_meeting(
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

        return False

    meeting = Meeting(
        **meeting_data
    )

    db.add(meeting)

    db.commit()

    db.refresh(meeting)

    return True


# ==========================================================
# TODAY
# ==========================================================

def get_today_meetings(
    db: Session,
    user_id: int
):

    today = datetime.now().date()

    meetings = (

        db.query(Meeting)

        .filter(
            Meeting.user_id == user_id
        )

        .all()

    )

    return [

        meeting

        for meeting in meetings

        if meeting.start_time.date() == today

    ]


# ==========================================================
# UPCOMING
# ==========================================================

def get_upcoming_meetings(
    db: Session,
    user_id: int
):

    now = datetime.now()

    return (

        db.query(Meeting)

        .filter(
            Meeting.user_id == user_id
        )

        .filter(
            Meeting.start_time > now
        )

        .order_by(
            Meeting.start_time
        )

        .all()

    )


# ==========================================================
# ANALYTICS
# ==========================================================

def total_meeting_hours(
    db: Session,
    user_id: int
):

    meetings = (

        db.query(Meeting)

        .filter(
            Meeting.user_id == user_id
        )

        .all()

    )

    return {

        "meeting_hours":

        calculate_total_meeting_hours(
            meetings
        )

    }


def get_conflicts(
    db: Session,
    user_id: int
):

    meetings = (

        db.query(Meeting)

        .filter(
            Meeting.user_id == user_id
        )

        .order_by(
            Meeting.start_time
        )

        .all()

    )

    return detect_conflicts(
        meetings
    )


def get_free_slots(
    db: Session,
    user_id: int
):

    meetings = (

        db.query(Meeting)

        .filter(
            Meeting.user_id == user_id
        )

        .order_by(
            Meeting.start_time
        )

        .all()

    )

    return calculate_free_slots(
        meetings
    )


def get_best_focus_window(
    db: Session,
    user_id: int
):

    meetings = (

        db.query(Meeting)

        .filter(
            Meeting.user_id == user_id
        )

        .order_by(
            Meeting.start_time
        )

        .all()

    )

    free_slots = calculate_free_slots(
        meetings
    )

    return calculate_best_focus_window(
        free_slots
    )


def get_meeting_analytics(
    db: Session,
    user_id: int
):

    meetings = (

        db.query(Meeting)

        .filter(
            Meeting.user_id == user_id
        )

        .order_by(
            Meeting.start_time
        )

        .all()

    )

    meeting_hours = calculate_total_meeting_hours(
        meetings
    )

    free_slots = calculate_free_slots(
        meetings
    )

    return {

        "meeting_hours": meeting_hours,

        "meeting_load": calculate_meeting_load(
            meeting_hours
        ),

        "total_meetings": len(
            meetings
        ),

        "conflicts": detect_conflicts(
            meetings
        ),

        "free_slots": free_slots,

        "best_focus_window": calculate_best_focus_window(
            free_slots
        )

    }

# ==========================================================
# TODAY'S SCHEDULE
# ==========================================================

def get_today_schedule(
    db: Session,
    user_id: int
):

    meetings = get_today_meetings(
        db,
        user_id
    )

    schedule = []

    for meeting in meetings:

        schedule.append({

            "title": meeting.title,

            "start": meeting.start_time.strftime("%H:%M"),

            "end": meeting.end_time.strftime("%H:%M"),

            "meeting_type": meeting.meeting_type,

            "location": meeting.location

        })

    return schedule