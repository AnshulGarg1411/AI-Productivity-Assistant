"""
Builds the rule-based morning brief dict, then hands it to the AI layer for
narration. Deliberately has zero dependency on dashboard_service or
morning_brief_service -- both of those depend on THIS module instead of on
each other, which is what keeps them from forming an import cycle (since
morning_brief_service.get_morning_brief() calls
dashboard_service.get_dashboard_data(), dashboard_service can't also import
morning_brief_service to build the brief itself).
"""
from datetime import datetime

from app.ai.morning_brief_agent import narrate_brief


def build_morning_brief_dict(
    user,
    unread_count: int,
    today_meetings_count: int,
    pending_tasks_count: int,
    today_tasks: list,
    focus,
    productivity_score: float,
    recommendations: list,
) -> dict:

    hour = datetime.now().hour

    greeting = "Good Morning"

    if hour >= 12:
        greeting = "Good Afternoon"

    if hour >= 18:
        greeting = "Good Evening"

    summary = [
        f"{unread_count} unread emails",
        f"{today_meetings_count} meetings today",
        f"{pending_tasks_count} pending tasks",
    ]

    top_priority = today_tasks[0].title if today_tasks else None

    focus_window = None

    if focus:
        focus_window = f"{focus.start} - {focus.end}"

    rule_based = {
        "greeting": f"{greeting}, {user.name}!",
        "summary": summary,
        "top_priority": top_priority,
        "focus_window": focus_window,
        "productivity_score": productivity_score,
        "recommendations": [item.title for item in recommendations],
    }

    return narrate_brief(rule_based)
