"""
Generates a draft reply to an email in a chosen tone. On-demand (called
when a user clicks "generate reply" on a specific email), not run in bulk
at sync time -- there's no single "right" reply to precompute, and running
this for every synced email regardless of whether the user ever reads it
would be wasted cost.
"""
import logging

from app.ai.gemini_client import generate_text
from app.core.config import settings
from app.models.email import Email

logger = logging.getLogger("app.ai")

VALID_TONES = {"formal", "friendly", "short", "detailed"}

TONE_INSTRUCTIONS = {
    "formal": "Write a formal, professional reply.",
    "friendly": "Write a warm, friendly, conversational reply.",
    "short": "Write a brief reply, at most 2-3 sentences.",
    "detailed": "Write a thorough, detailed reply covering all points raised.",
}


class SmartReplyUnavailable(Exception):
    """Raised when reply generation can't run (e.g. no Gemini key)."""


def generate_reply(email: Email, tone: str = "friendly") -> str:
    if not settings.AI_FEATURES_ENABLED:
        raise SmartReplyUnavailable(
            "Smart reply requires a GEMINI_API_KEY to be configured."
        )

    tone = tone if tone in VALID_TONES else "friendly"

    content = email.body or email.snippet or ""

    prompt = (
        f"Original email:\n"
        f"From: {email.sender}\n"
        f"Subject: {email.subject}\n\n"
        f"{content[:3000]}\n\n"
        f"{TONE_INSTRUCTIONS[tone]} Write only the reply body, no subject "
        f"line, no placeholder brackets like [Your Name]."
    )

    result = generate_text(
        prompt,
        system_instruction=(
            "You draft email replies for a personal productivity assistant. "
            "Write only the reply text itself, nothing else."
        ),
    )

    if not result:
        raise SmartReplyUnavailable(
            "Reply generation failed. Please try again."
        )

    return result.strip()
