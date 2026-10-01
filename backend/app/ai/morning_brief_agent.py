"""
Takes the rule-based morning brief and asks Gemini to rewrite the greeting
and summary as natural, conversational prose.

Deliberately narrow in two ways:
1. top_priority, focus_window, and productivity_score are facts computed by
   real logic and are never handed to the LLM to rewrite.
2. recommendations are NOT narrated here -- they're already enhanced once,
   upstream, by app/ai/recommendation_agent.py (reused for both the
   dashboard's recommendation cards and this brief), so narrating them a
   second time here would be a redundant Gemini call touching the same
   text twice.

If Gemini is unavailable or the call fails, the original rule-based dict
is returned unchanged, so this can never break the Morning Brief feature --
it can only make it sound nicer.
"""
import logging

from app.ai.groq_client import generate_json
from app.core.config import settings

logger = logging.getLogger("app.ai")

NARRATION_SCHEMA = {
    "type": "object",
    "properties": {
        "greeting": {"type": "string"},
        "summary": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": ["greeting", "summary"],
}

SYSTEM_INSTRUCTION = (
    "You rewrite a productivity assistant's morning greeting and summary "
    "in a warm, concise, conversational tone. You are given exact facts "
    "(counts, times) -- rephrase them naturally but never invent new "
    "numbers or facts that weren't given to you. Keep the same number of "
    "summary lines as the input. Keep each line short, suitable for a "
    "dashboard card."
)


def narrate_brief(rule_based_brief: dict) -> dict:
    """
    rule_based_brief must have: greeting, summary (list[str]), top_priority,
    focus_window, productivity_score, recommendations (list[str]).
    Returns a dict with the same shape -- greeting/summary narrated if
    possible, everything else passed through unchanged.
    """
    if not settings.AI_FEATURES_ENABLED:
        return rule_based_brief

    prompt = (
        f"Facts:\n"
        f"- Original greeting: {rule_based_brief['greeting']}\n"
        f"- Summary points: {rule_based_brief['summary']}\n"
        f"- Top priority task: {rule_based_brief.get('top_priority') or 'none'}\n"
        f"- Focus window: {rule_based_brief.get('focus_window') or 'none'}\n"
        f"- Productivity score: {rule_based_brief['productivity_score']}/100\n\n"
        "Rewrite the greeting and summary naturally."
    )

    result = generate_json(
        prompt,
        NARRATION_SCHEMA,
        system_instruction=SYSTEM_INSTRUCTION,
    )

    if not result:
        return rule_based_brief

    try:
        return {
            **rule_based_brief,
            "greeting": result.get("greeting") or rule_based_brief["greeting"],
            "summary": result.get("summary") or rule_based_brief["summary"],
        }
    except Exception:
        logger.exception("Failed to merge narrated brief, using rule-based version")
        return rule_based_brief
