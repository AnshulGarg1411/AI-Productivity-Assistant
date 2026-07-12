"""
Thin wrapper around the Gemini API for structured (JSON) generation.

Design principle: every function here returns None on any failure --
missing API key, network error, quota, malformed response -- instead of
raising. Callers (task extraction, morning brief narration) always have a
deterministic fallback and must never let an AI failure break a real
feature (email sync, calendar sync, the dashboard).
"""
import json
import logging

from app.core.config import settings

logger = logging.getLogger("app.ai")

_client = None


def _get_client():
    """Lazily construct the Gemini client. Returns None if unavailable."""
    global _client

    if not settings.AI_FEATURES_ENABLED:
        return None

    if _client is not None:
        return _client

    try:
        from google import genai

        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
        return _client

    except Exception:
        logger.exception("Failed to initialize Gemini client")
        return None


def generate_json(
    prompt: str,
    response_schema: dict,
    system_instruction: str | None = None,
    temperature: float = 0.2,
):
    """
    Ask Gemini for a response matching response_schema (a JSON Schema dict),
    parsed and returned as a Python dict. Returns None on any failure.
    """
    client = _get_client()

    if client is None:
        return None

    try:
        from google.genai import types

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema,
            temperature=temperature,
            system_instruction=system_instruction,
        )

        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=config,
        )

        return json.loads(response.text)

    except Exception:
        logger.exception("Gemini generate_json call failed")
        return None


def generate_text(
    prompt: str,
    system_instruction: str | None = None,
    temperature: float = 0.4,
) -> str | None:
    """
    Plain free-form text generation (no JSON schema) -- used where the
    output is prose meant for a human to read as-is (e.g. a reply draft),
    where forcing JSON encoding would just add escaping overhead for no
    benefit. Returns None on any failure.
    """
    client = _get_client()

    if client is None:
        return None

    try:
        from google.genai import types

        config = types.GenerateContentConfig(
            temperature=temperature,
            system_instruction=system_instruction,
        )

        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=config,
        )

        return response.text

    except Exception:
        logger.exception("Gemini generate_text call failed")
        return None
