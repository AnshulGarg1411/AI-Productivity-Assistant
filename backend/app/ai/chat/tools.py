"""
LangChain tools binding the chat agent to the app's EXISTING services. This
is the "one supervisor + tools" architecture: rather than separate Task
Agent / Calendar Agent / Recommendation Agent modules, each capability from
the original agent list is exposed here as a tool the chat agent can call.

Tools are built per-request via build_tools(db, user) rather than defined
as bare module-level functions, because each one needs the current user's
db session and identity closed over -- this is a multi-user backend, so a
tool must never be able to act on anyone but the authenticated caller.
"""
from datetime import datetime

from langchain_core.tools import tool
from sqlalchemy.orm import Session

from app.models.user import User
from app.enums.task_enum import TaskSource

from app.services.task_service import (
    get_all_tasks,
    get_pending_tasks,
    get_completed_tasks,
    get_overdue_tasks,
    create_task,
    complete_task,
    delete_task,
)
from app.services.meeting_service import (
    get_today_meetings,
    get_upcoming_meetings,
    get_all_meetings,
    create_meeting,
    get_meeting_analytics,
)
from app.services.email_service import (
    get_unread_emails,
    get_important_emails,
    get_starred_emails,
    get_all_emails,
    search_emails,
)
from app.services.dashboard_service import get_dashboard_data


def _format_tasks(tasks) -> str:
    if not tasks:
        return "No tasks found."
    return "\n".join(
        f"- [id={t.id}] {t.title} (priority={t.priority.value}, "
        f"status={t.status.value}, due={t.due_date.date()})"
        for t in tasks
    )


def _format_meetings(meetings) -> str:
    if not meetings:
        return "No meetings found."
    return "\n".join(
        f"- [id={m.id}] {m.title} ({m.start_time.strftime('%Y-%m-%d %H:%M')} "
        f"- {m.end_time.strftime('%H:%M')}, status={m.status.value})"
        for m in meetings
    )


def _format_emails(emails) -> str:
    if not emails:
        return "No emails found."
    return "\n".join(
        f"- [id={e.id}] From {e.sender}: \"{e.subject}\" "
        f"(unread={e.unread}, important={e.importance})"
        for e in emails[:15]
    )


def build_tools(db: Session, user: User):
    """Returns the list of tools bound to this specific user's session."""

    @tool
    def list_tasks(status: str = "all") -> str:
        """List the user's tasks. status must be one of: all, pending,
        completed, overdue."""

        if status == "pending":
            tasks = get_pending_tasks(db, user.id)
        elif status == "completed":
            tasks = get_completed_tasks(db, user.id)
        elif status == "overdue":
            tasks = get_overdue_tasks(db, user.id)
        else:
            tasks = get_all_tasks(db, user.id)

        return _format_tasks(tasks)

    @tool
    def create_task_tool(
        title: str,
        category: str,
        priority: str,
        due_date: str,
        estimated_minutes: int = 30,
    ) -> str:
        """Create a new task. category must be one of WORK, STUDY, PERSONAL,
        HEALTH. priority must be one of LOW, MEDIUM, HIGH. due_date must be
        an ISO 8601 date/time string."""

        try:
            parsed_due = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        except ValueError:
            return f"Could not parse due_date '{due_date}'. Use ISO 8601 format."

        task = create_task(
            db,
            {
                "user_id": user.id,
                "title": title,
                "category": category,
                "priority": priority,
                "due_date": parsed_due,
                "estimated_minutes": estimated_minutes,
                "source": TaskSource.AI,
            },
        )

        return f"Created task [id={task.id}] \"{task.title}\", due {task.due_date.date()}."

    @tool
    def complete_task_tool(task_id: int, actual_minutes: int = 30) -> str:
        """Mark a task as completed, given its id."""

        task = complete_task(db, user.id, task_id, actual_minutes)

        if task is None:
            return f"No task with id {task_id} found."

        return f"Marked task [id={task.id}] \"{task.title}\" as completed."

    @tool
    def delete_task_tool(task_id: int) -> str:
        """Delete a task, given its id."""

        deleted = delete_task(db, user.id, task_id)

        if not deleted:
            return f"No task with id {task_id} found."

        return f"Deleted task {task_id}."

    @tool
    def list_meetings(when: str = "upcoming") -> str:
        """List the user's meetings. when must be one of: today, upcoming,
        all."""

        if when == "today":
            meetings = get_today_meetings(db, user.id)
        elif when == "all":
            meetings = get_all_meetings(db, user.id)
        else:
            meetings = get_upcoming_meetings(db, user.id)

        return _format_meetings(meetings)

    @tool
    def create_meeting_tool(
        title: str,
        start_time: str,
        end_time: str,
        meeting_type: str = "ONLINE",
    ) -> str:
        """Create a new meeting. start_time and end_time must be ISO 8601
        date/time strings. meeting_type must be ONLINE or OFFLINE."""

        try:
            start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            end = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
        except ValueError:
            return "Could not parse start_time/end_time. Use ISO 8601 format."

        meeting = create_meeting(
            db,
            {
                "user_id": user.id,
                "title": title,
                "start_time": start,
                "end_time": end,
                "meeting_type": meeting_type,
                "status": "CONFIRMED",
            },
        )

        return f"Created meeting [id={meeting.id}] \"{meeting.title}\"."

    @tool
    def get_meeting_analytics_tool() -> str:
        """Get the user's meeting analytics: conflicts, free time slots,
        best focus window, and total meeting load."""

        analytics = get_meeting_analytics(db, user.id)

        lines = [
            f"Meeting hours: {analytics['meeting_hours']:.1f}",
            f"Meeting load: {analytics['meeting_load']}",
        ]

        if analytics["conflicts"]:
            lines.append(f"Conflicts: {len(analytics['conflicts'])} found")

        if analytics.get("best_focus_window"):
            fw = analytics["best_focus_window"]
            lines.append(f"Best focus window: {fw['start']} - {fw['end']}")

        return "\n".join(lines)

    @tool
    def list_emails(filter: str = "unread") -> str:
        """List the user's emails. filter must be one of: unread, important,
        starred, all."""

        if filter == "important":
            emails = get_important_emails(db, user.id)
        elif filter == "starred":
            emails = get_starred_emails(db, user.id)
        elif filter == "all":
            emails = get_all_emails(db, user.id)
        else:
            emails = get_unread_emails(db, user.id)

        return _format_emails(emails)

    @tool
    def search_emails_tool(query: str) -> str:
        """Search the user's emails by subject, sender, or content."""

        emails = search_emails(db, user.id, query)
        return _format_emails(emails)

    @tool
    def get_recommendations() -> str:
        """Get the user's current productivity recommendations and score."""

        dashboard = get_dashboard_data(db, user)

        lines = [f"Productivity score: {dashboard.productivity.score}/100"]

        for rec in dashboard.recommendations:
            lines.append(f"- {rec.title}: {rec.description}")

        return "\n".join(lines)

    return [
        list_tasks,
        create_task_tool,
        complete_task_tool,
        delete_task_tool,
        list_meetings,
        create_meeting_tool,
        get_meeting_analytics_tool,
        list_emails,
        search_emails_tool,
        get_recommendations,
    ]
