"""
Reads a synced email and asks Gemini for: a short summary, a predicted
category (replacing reliance on Gmail's own labels), and a HIGH/MEDIUM/LOW
priority classification (replacing the blunt importance boolean). One call
per email, all three at once, rather than three separate calls.

Called from gmail_service.sync_gmail() right after new emails are
committed, same pattern as task_extraction_agent -- bounded batch size,
never lets a failure break the sync.
"""
import logging

from sqlalchemy.orm import Session

from app.ai.groq_client import generate_json
from app.core.config import settings
from app.models.email import Email

logger = logging.getLogger("app.ai")

MAX_ANALYSES_PER_SYNC = 20

VALID_CATEGORIES = {
    "WORK",
    "COLLEGE",
    "FINANCE",
    "SHOPPING",
    "TRAVEL",
    "SOCIAL",
    "OTHER",
}

VALID_PRIORITIES = {"HIGH", "MEDIUM", "LOW"}

EMAIL_ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {
            "type": "string",
            "description": (
                "1-2 sentence summary covering purpose, any deadline, and "
                "whether the recipient needs to take action."
            ),
        },
        "category": {
            "type": "string",
            "enum": sorted(VALID_CATEGORIES),
        },
        "priority": {
            "type": "string",
            "enum": sorted(VALID_PRIORITIES),
            "description": (
                "HIGH = needs attention today/urgent, MEDIUM = needs a "
                "response but not urgent, LOW = FYI/no action needed."
            ),
        },
    },
    "required": ["summary", "category", "priority"],
}

SYSTEM_INSTRUCTION = (
    "You analyze emails for a personal productivity assistant. Be concise "
    "and factual in the summary -- state what the email is about and "
    "whether the recipient needs to do something, don't editorialize."
)


def analyze_email(db: Session, email: Email) -> bool:
    """Populates email.ai_summary/category/ai_priority in place. Returns
    True if it was analyzed, False if skipped (already analyzed, or AI
    disabled) or failed."""

    if not settings.AI_FEATURES_ENABLED:
        return False

    if email.ai_summary:
        # Already analyzed -- don't re-spend a Gemini call on re-sync.
        return False

    content = email.body or email.snippet or ""

    prompt = (
        f"Subject: {email.subject}\n"
        f"From: {email.sender}\n\n"
        f"Body:\n{content[:3000]}"
    )

    result = generate_json(
        prompt,
        EMAIL_ANALYSIS_SCHEMA,
        system_instruction=SYSTEM_INSTRUCTION,
    )

    if not result:
        return False

    category = result.get("category")
    priority = result.get("priority")

    try:
        email.ai_summary = result.get("summary") or None
        email.category = category if category in VALID_CATEGORIES else email.category
        email.ai_priority = priority if priority in VALID_PRIORITIES else None

        db.add(email)
        db.commit()

        return True

    except Exception:
        logger.exception("Failed to save email analysis for email %s", email.id)
        db.rollback()
        return False


def analyze_new_emails(db: Session, emails: list[Email]):
    """Runs analysis over a bounded batch of newly-synced emails. Never
    raises -- logs and continues past individual failures."""

    for email in emails[:MAX_ANALYSES_PER_SYNC]:
        try:
            analyze_email(db, email)
        except Exception:
            logger.exception(
                "Email analysis crashed for email %s", getattr(email, "id", "?")
            )
