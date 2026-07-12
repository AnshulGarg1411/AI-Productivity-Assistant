from datetime import timedelta

from datetime import (
    datetime,
    timedelta,
    time
)

WORK_START = time(9, 0)

WORK_END = time(18, 0)
def calculate_total_meeting_hours(
    meetings
):

    meetings = get_today_meetings_only(
        meetings
    )

    total = timedelta()

    for meeting in meetings:

        total += (

            meeting.end_time

            -

            meeting.start_time

        )

    return round(

        total.total_seconds() / 3600,

        2

    )


def detect_conflicts(
    meetings
):

    meetings = get_today_meetings_only(
        meetings
    )

    meetings.sort(

        key=lambda meeting:

        meeting.start_time

    )

    conflicts = []

    for i in range(

        len(meetings) - 1

    ):

        current = meetings[i]

        nxt = meetings[i + 1]

        if current.end_time > nxt.start_time:

            conflicts.append({

                "meeting1": current.title,

                "meeting2": nxt.title

            })

    return conflicts


def calculate_free_slots(
    meetings
):

    meetings = get_today_meetings_only(
        meetings
    )

    meetings.sort(
        key=lambda meeting: meeting.start_time
    )

    free_slots = []

    today = datetime.now().date()

    work_start = datetime.combine(
        today,
        WORK_START
    )

    work_end = datetime.combine(
        today,
        WORK_END
    )

    # ---------------------------------
    # No meetings today
    # ---------------------------------

    if len(meetings) == 0:

        duration = work_end - work_start

        return [

            {

                "start": work_start,

                "end": work_end,

                "duration_minutes":
                    int(
                        duration.total_seconds() / 60
                    )

            }

        ]

    # ---------------------------------
    # Before first meeting
    # ---------------------------------

    if meetings[0].start_time > work_start:

        duration = (

            meetings[0].start_time

            -

            work_start

        )

        free_slots.append({

            "start": work_start,

            "end": meetings[0].start_time,

            "duration_minutes":

                int(

                    duration.total_seconds() / 60

                )

        })

    # ---------------------------------
    # Between meetings
    # ---------------------------------

    for i in range(

        len(meetings) - 1

    ):

        start = meetings[i].end_time

        end = meetings[i + 1].start_time

        if end > start:

            duration = end - start

            free_slots.append({

                "start": start,

                "end": end,

                "duration_minutes":

                    int(

                        duration.total_seconds() / 60

                    )

            })

    # ---------------------------------
    # After last meeting
    # ---------------------------------

    if meetings[-1].end_time < work_end:

        duration = (

            work_end

            -

            meetings[-1].end_time

        )

        free_slots.append({

            "start": meetings[-1].end_time,

            "end": work_end,

            "duration_minutes":

                int(

                    duration.total_seconds() / 60

                )

        })

    return free_slots


def calculate_best_focus_window(
    free_slots
):

    if len(free_slots) == 0:

        return None

    return max(

        free_slots,

        key=lambda slot:

            slot["duration_minutes"]

    )
def calculate_meeting_load(
    meeting_hours
):

    if meeting_hours < 2:

        return "LOW"

    elif meeting_hours < 5:

        return "MEDIUM"

    elif meeting_hours < 7:

        return "HIGH"

    return "OVERLOADED"
def get_today_meetings_only(
    meetings
):

    today = datetime.now().date()

    return [

        meeting

        for meeting in meetings

        if meeting.start_time.date() == today

    ]