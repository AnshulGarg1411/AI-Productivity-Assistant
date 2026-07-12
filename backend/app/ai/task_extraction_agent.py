"""
Reads a synced email or meeting and asks Gemini whether it implies an
actionable task -- if so, creates a real Task row via the existing
task_service, linked back to its source via source_email_id/source_meeting_id
(see app/models/task.py for why those columns exist).

Called from gmail_service.sync_gmail() and calendar_service.sync_calendar()
right after new items are committed. Every entry point here is wrapped so a
single extraction failure (bad LLM response, network hiccup) can never take
down an email/calendar sync -- it just skips that one item.
"""
import logging
from datetime import timedelta

from sqlalchemy.orm import Session

from app.ai.gemini_client import generate_json
from app.core.config import settings
from app.models.task import Task
from app.models.email import Email
from app.models.meeting import Meeting
from app.enums.task_enum import TaskPriority, TaskCategory, TaskSource
from app.services.task_service import create_task

logger = logging.getLogger("app.ai")

# Cap how many newly-synced items we run extraction on per sync call, so a
# first-time sync of a large inbox/calendar doesn't fire off dozens of LLM
# calls in one request.
MAX_EXTRACTIONS_PER_SYNC = 20

TASK_EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "has_task": {"type": "boolean"},
        "title": {"type": "string"},
        "due_date": {
            "type": "string",
            "description": "ISO 8601 date/time, or empty string if none is implied",
        },
        "priority": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH"]},
        "category": {
            "type": "string",
            "enum": ["WORK", "STUDY", "PERSONAL", "HEALTH"],
        },
    },
    "required": ["has_task", "title", "priority", "category"],
}

SYSTEM_INSTRUCTION = (
    "You extract actionable tasks from emails and meeting descriptions for "
    "a personal productivity assistant. Only set has_task to true if there "
    "is a genuinely actionable item with an implied deadline or clear next "
    "step (e.g. 'submit the assignment by Friday', 'send over the invoice'). "
    "Newsletters, notifications, FYI messages, and purely informational "
    "meetings should have has_task set to false. Be conservative -- a "
    "missed task is better than a spammy false positive."
)


def _parse_priority(value: str) -> TaskPriority:
    try:
        return TaskPriority(value)
    except ValueError:
        return TaskPriority.MEDIUM


def _parse_category(value: str) -> TaskCategory:
    try:
        return TaskCategory(value)
    except ValueError:
        return TaskCategory.WORK


def _existing_task_for_email(db: Session, email_id: int) -> bool:
    return (
        db.query(Task)
        .filter(Task.source_email_id == email_id)
        .first()
        is not None
    )


def _existing_task_for_meeting(db: Session, meeting_id: int) -> bool:
    return (
        db.query(Task)
        .filter(Task.source_meeting_id == meeting_id)
        .first()
        is not None
    )


def create_task_from_email(db: Session, email: Email):
    """Returns the created Task, or None if no task was warranted/created."""

    if not settings.AI_FEATURES_ENABLED:
        return None

    if _existing_task_for_email(db, email.id):
        return None

    content = email.body or email.snippet or ""

    prompt = (
        f"Subject: {email.subject}\n"
        f"From: {email.sender}\n"
        f"Received: {email.received_at.isoformat()}\n\n"
        f"Body:\n{content[:3000]}"
    )

    result = generate_json(
        prompt,
        TASK_EXTRACTION_SCHEMA,
        system_instruction=SYSTEM_INSTRUCTION,
    )

    if not result or not result.get("has_task"):
        return None

    due_date = _resolve_due_date(
        result.get("due_date"),
        fallback=email.received_at + timedelta(days=2),
    )

    try:
        return create_task(
            db,
            {
                "user_id": email.user_id,
                "title": result["title"][:255],
                "description": f"Auto-created from email: \"{email.subject}\"",
                "category": _parse_category(result["category"]),
                "priority": _parse_priority(result["priority"]),
                "due_date": due_date,
                "estimated_minutes": 30,
                "source": TaskSource.EMAIL,
                "source_email_id": email.id,
            },
        )
    except Exception:
        logger.exception(
            "Failed to create task from email %s", email.id
        )
        return None


def create_task_from_meeting(db: Session, meeting: Meeting):
    """Returns the created Task, or None if no task was warranted/created."""

    if not settings.AI_FEATURES_ENABLED:
        return None

    if _existing_task_for_meeting(db, meeting.id):
        return None

    prompt = (
        f"Meeting title: {meeting.title}\n"
        f"Starts: {meeting.start_time.isoformat()}\n"
        f"Description:\n{(meeting.description or '')[:2000]}"
    )

    result = generate_json(
        prompt,
        TASK_EXTRACTION_SCHEMA,
        system_instruction=(
            SYSTEM_INSTRUCTION
            + " For meetings, only flag a task if there's clear prep work "
            "implied (e.g. 'bring the slides', 'review the doc beforehand') "
            "-- routine meetings with no prep should have has_task false."
        ),
    )

    if not result or not result.get("has_task"):
        return None

    due_date = _resolve_due_date(
        result.get("due_date"),
        fallback=meeting.start_time,
    )

    try:
        return create_task(
            db,
            {
                "user_id": meeting.user_id,
                "title": result["title"][:255],
                "description": f"Auto-created from meeting: \"{meeting.title}\"",
                "category": _parse_category(result["category"]),
                "priority": _parse_priority(result["priority"]),
                "due_date": due_date,
                "estimated_minutes": 30,
                "source": TaskSource.CALENDAR,
                "source_meeting_id": meeting.id,
            },
        )
    except Exception:
        logger.exception(
            "Failed to create task from meeting %s", meeting.id
        )
        return None


def _resolve_due_date(raw_value, fallback):
    if not raw_value:
        return fallback

    try:
        from datetime import datetime

        return datetime.fromisoformat(raw_value.replace("Z", "+00:00"))
    except Exception:
        return fallback


def extract_tasks_from_new_emails(db: Session, emails: list[Email]):
    """Runs extraction over a bounded batch of newly-synced emails.
    Never raises -- logs and continues past individual failures."""

    for email in emails[:MAX_EXTRACTIONS_PER_SYNC]:
        try:
            create_task_from_email(db, email)
        except Exception:
            logger.exception(
                "Task extraction crashed for email %s", getattr(email, "id", "?")
            )


def extract_tasks_from_new_meetings(db: Session, meetings: list[Meeting]):
    """Runs extraction over a bounded batch of newly-synced meetings.
    Never raises -- logs and continues past individual failures."""

    for meeting in meetings[:MAX_EXTRACTIONS_PER_SYNC]:
        try:
            create_task_from_meeting(db, meeting)
        except Exception:
            logger.exception(
                "Task extraction crashed for meeting %s",
                getattr(meeting, "id", "?"),
            )
