from app.schemas.dashboard_schema import (
    ProductivityResponse
)


def calculate_productivity_score(
    unread_emails: int,
    important_emails: int,
    meeting_hours: float,
    meeting_conflicts: int,
    pending_tasks: int,
    overdue_tasks: int,
    high_priority_tasks: int,
    focus_minutes: int
) -> ProductivityResponse:

    score = 100

    # ----------------------------------
    # Emails
    # ----------------------------------

    score -= min(
        unread_emails * 2,
        20
    )

    score -= min(
        important_emails * 3,
        15
    )

    # ----------------------------------
    # Meetings
    # ----------------------------------

    if meeting_hours > 6:

        score -= 15

    score -= min(
        meeting_conflicts * 10,
        20
    )

    # ----------------------------------
    # Tasks
    # ----------------------------------

    score -= min(
        pending_tasks,
        10
    )

    score -= min(
        overdue_tasks * 5,
        20
    )

    score -= min(
        high_priority_tasks * 3,
        15
    )

    # ----------------------------------
    # Focus Bonus
    # ----------------------------------

    if focus_minutes >= 120:

        score += 10

    score = max(
        0,
        min(
            100,
            score
        )
    )

    # ----------------------------------
    # Productivity Level
    # ----------------------------------

    if score >= 85:

        status = "Excellent"

    elif score >= 70:

        status = "Good"

    elif score >= 50:

        status = "Average"

    else:

        status = "Needs Attention"

    return ProductivityResponse(

        score=score,

        status=status

    )