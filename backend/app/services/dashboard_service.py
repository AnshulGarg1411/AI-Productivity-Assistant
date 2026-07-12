from sqlalchemy.orm import Session

from app.models.user import User

from app.services.email_service import (
    get_all_emails,
    get_unread_emails,
    get_important_emails,
     get_urgent_emails
)
from app.services.meeting_service import (
    get_today_meetings,
    get_upcoming_meetings,
    get_meeting_analytics,
    get_best_focus_window,
    get_today_schedule
)
from app.schemas.dashboard_schema import (
    
    TaskDashboardResponse
)

from app.services.brief_builder import build_morning_brief_dict
from app.services.task_service import (
    get_pending_tasks,
    get_completed_tasks,
    get_overdue_tasks,
    get_high_priority_tasks,
    get_today_tasks_card,
    get_upcoming_deadlines
)

from app.analytics.productivity_score import (
    calculate_productivity_score
)

from app.recommendation.recommendation_engine import (
    generate_recommendations
)
from app.ai.recommendation_agent import enhance_recommendations

from app.schemas.dashboard_schema import (
    DashboardResponse,
    UserDashboardResponse,
    EmailDashboardResponse,
    MeetingDashboardResponse,
    FocusWindowDashboardResponse
)


def get_dashboard_data(
    db: Session,
    user: User
):

    # ------------------------
    # Emails
    # ------------------------

    emails = get_all_emails(
        db,
        user.id
    )

    unread = get_unread_emails(
        db,
        user.id
    )

    important = get_important_emails(
        db,
        user.id
    )
    urgent_emails = get_urgent_emails(
    db,
    user.id
    )
    # ------------------------
    # Meetings
    # ------------------------

    today_meetings = get_today_meetings(
        db,
        user.id
    )
    today_schedule = get_today_schedule(
    db,
    user.id
    )
    upcoming = get_upcoming_meetings(
        db,
        user.id
    )

    meeting_analytics = get_meeting_analytics(
        db,
        user.id
    )

    focus_window = get_best_focus_window(
        db,
        user.id
    )
 
    # ------------------------
    # Tasks
    # ------------------------

    pending = get_pending_tasks(
        db,
        user.id
    )

    completed = get_completed_tasks(
        db,
        user.id
    )

    overdue = get_overdue_tasks(
        db,
        user.id
    )

    high_priority = get_high_priority_tasks(
        db,
        user.id
    )
    today_tasks = get_today_tasks_card(
    db,
    user.id
    )
    upcoming_deadlines = get_upcoming_deadlines(

    db,

    user.id

)
    # ------------------------
    # Productivity
    # ------------------------

    focus_minutes = 0

    if focus_window:

        focus_minutes = focus_window[
            "duration_minutes"
        ]

    productivity = calculate_productivity_score(

        unread_emails=len(unread),

        important_emails=len(important),

        meeting_hours=meeting_analytics["meeting_hours"],

        meeting_conflicts=len(
            meeting_analytics["conflicts"]
        ),

        pending_tasks=len(pending),

        overdue_tasks=len(overdue),

        high_priority_tasks=len(
            high_priority
        ),

        focus_minutes=focus_minutes

    )

    # ------------------------
    # Recommendations
    # ------------------------

    recommendations = generate_recommendations(

        unread_emails=len(unread),

        important_emails=len(important),

        meeting_hours=meeting_analytics["meeting_hours"],

        upcoming_meetings=len(upcoming),

        pending_tasks=len(pending),

        overdue_tasks=len(overdue),

        high_priority_tasks=len(
            high_priority
        ),

        focus_minutes=focus_minutes

    )

    # AI enhancement (rewords title/description only -- see
    # app/ai/recommendation_agent.py for the guarantees around this).
    # Falls back to the rule-based list unchanged if AI is disabled/fails.
    recommendations = enhance_recommendations(recommendations)

    # ------------------------
    # Focus
    # ------------------------

    focus = None

    if focus_window:

        focus = FocusWindowDashboardResponse(

            start=focus_window[
                "start"
            ].strftime("%H:%M"),

            end=focus_window[
                "end"
            ].strftime("%H:%M"),

            duration_minutes=focus_window[
                "duration_minutes"
            ]

        )

    # ------------------------
    # Morning Brief
    # ------------------------
    #
    # Built from the same data already computed above, via a shared helper
    # (app/services/brief_builder.py) rather than calling
    # morning_brief_service directly -- that module imports this one, so a
    # direct import here would be circular.

    morning_brief = build_morning_brief_dict(
        user=user,
        unread_count=len(unread),
        today_meetings_count=len(today_meetings),
        pending_tasks_count=len(pending),
        today_tasks=today_tasks,
        focus=focus,
        productivity_score=productivity.score,
        recommendations=recommendations,
    )

    # ------------------------
    # Final Dashboard
    # ------------------------

    return DashboardResponse(

        user=UserDashboardResponse(

            id=user.id,

            name=user.name,

            email=user.email

        ),

        emails=EmailDashboardResponse(

            total=len(emails),

            unread=len(unread),

            important=len(important)

        ),
        urgent_emails=[
    {
        "id": email.id,

        "sender": email.sender,

        "subject": email.subject,

        "snippet": email.snippet,

        "received_at": email.received_at,

        "unread": email.unread,

        "importance": email.importance,

        "has_attachment": email.has_attachment
    }

    for email in urgent_emails
],
upcoming_deadlines=[

    {

        "title": task.title,

        "due_date": task.due_date,

        "priority": task.priority

    }

    for task in upcoming_deadlines

],
        meetings=MeetingDashboardResponse(

            today=len(today_meetings),

            upcoming=len(upcoming),

            meeting_hours=meeting_analytics[
                "meeting_hours"
            ]

        ),
        today_tasks=[

    {

        "title": task.title,

        "priority": task.priority,

        "status": task.status,

        "due_date": task.due_date,

        "estimated_minutes": task.estimated_minutes

    }

    for task in today_tasks

],
        tasks=TaskDashboardResponse(

    pending=len(
        pending
    ),

    completed=len(
        completed
    ),

    overdue=len(
        overdue
    ),

    high_priority=len(
        high_priority
    )

),
        today_schedule=today_schedule,

        focus=focus,

        productivity=productivity,

        recommendations=recommendations,
        morning_brief=morning_brief

    )