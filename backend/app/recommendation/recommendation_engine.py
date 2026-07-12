from app.schemas.dashboard_schema import (
    RecommendationResponse
)


def generate_recommendations(

    unread_emails: int,

    important_emails: int,

    meeting_hours: float,

    upcoming_meetings: int,

    pending_tasks: int,

    overdue_tasks: int,

    high_priority_tasks: int,

    focus_minutes: int

):

    recommendations = []

    # ==========================================
    # EMAILS
    # ==========================================

    if important_emails > 0:

        recommendations.append(

            RecommendationResponse(

                title="Reply to Important Emails",

                description=(
                    f"You have {important_emails} "
                    "important unread emails."
                ),

                priority="HIGH"

            )

        )

    elif unread_emails >= 10:

        recommendations.append(

            RecommendationResponse(

                title="Clean Your Inbox",

                description=(
                    "You have many unread emails."
                ),

                priority="MEDIUM"

            )

        )

    # ==========================================
    # TASKS
    # ==========================================

    if overdue_tasks > 0:

        recommendations.append(

            RecommendationResponse(

                title="Complete Overdue Tasks",

                description=(
                    f"{overdue_tasks} task(s) "
                    "are overdue."
                ),

                priority="HIGH"

            )

        )

    if high_priority_tasks > 0:

        recommendations.append(

            RecommendationResponse(

                title="Finish High Priority Tasks",

                description=(
                    f"{high_priority_tasks} "
                    "high priority task(s) "
                    "are pending."
                ),

                priority="HIGH"

            )

        )

    elif pending_tasks >= 8:

        recommendations.append(

            RecommendationResponse(

                title="Reduce Pending Tasks",

                description=(
                    "You have too many pending tasks."
                ),

                priority="MEDIUM"

            )

        )

    # ==========================================
    # MEETINGS
    # ==========================================

    if meeting_hours >= 6:

        recommendations.append(

            RecommendationResponse(

                title="Meeting Overload",

                description=(
                    "You have a meeting-heavy day."
                ),

                priority="MEDIUM"

            )

        )

    if upcoming_meetings > 0:

        recommendations.append(

            RecommendationResponse(

                title="Prepare for Upcoming Meetings",

                description=(
                    f"{upcoming_meetings} "
                    "meeting(s) scheduled."
                ),

                priority="LOW"

            )

        )

    # ==========================================
    # FOCUS
    # ==========================================

    if focus_minutes >= 120:

        recommendations.append(

            RecommendationResponse(

                title="Schedule Deep Work",

                description=(
                    "You have a long focus window."
                ),

                priority="LOW"

            )

        )

    # ==========================================
    # Everything Looks Good
    # ==========================================

    if len(recommendations) == 0:

        recommendations.append(

            RecommendationResponse(

                title="Great Job!",

                description=(
                    "Everything looks under control."
                ),

                priority="LOW"

            )

        )

    return recommendations