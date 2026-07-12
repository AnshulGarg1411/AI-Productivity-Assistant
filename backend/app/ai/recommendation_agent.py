"""
Takes the rule-based recommendations (app/recommendation/recommendation_engine.py)
and asks Gemini to rewrite their title/description to be more specific and
actionable, given the user's actual context. Deliberately narrow: the rule
engine still decides WHICH recommendations exist and their priority --
Gemini only rewrites the wording of ones that already exist. It can never
add, remove, or reorder recommendations, and it can never change priority.

Used once per dashboard load, and the result is reused both for the
dashboard's recommendation cards and for the morning brief's recommendation
list -- see app/services/dashboard_service.py and brief_builder.py -- so
this is the only LLM call that touches recommendation text.
"""
import logging

from app.ai.gemini_client import generate_json
from app.core.config import settings
from app.schemas.dashboard_schema import RecommendationResponse

logger = logging.getLogger("app.ai")

ENHANCEMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "recommendations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["title", "description"],
            },
        },
    },
    "required": ["recommendations"],
}

SYSTEM_INSTRUCTION = (
    "You rewrite productivity recommendations to be more specific and "
    "actionable, based on the user's real data. You are given a fixed list "
    "of recommendations in a fixed order -- return exactly the same number "
    "of items, in the same order, only rewriting title/description. Do "
    "not add, remove, reorder, or invent new recommendations, and do not "
    "invent facts/numbers that weren't given to you."
)


def enhance_recommendations(
    recommendations: list[RecommendationResponse],
) -> list[RecommendationResponse]:

    if not settings.AI_FEATURES_ENABLED or not recommendations:
        return recommendations

    prompt = "Recommendations:\n" + "\n".join(
        f"{i + 1}. [{r.priority}] {r.title}: {r.description}"
        for i, r in enumerate(recommendations)
    )

    result = generate_json(
        prompt,
        ENHANCEMENT_SCHEMA,
        system_instruction=SYSTEM_INSTRUCTION,
    )

    if not result:
        return recommendations

    enhanced_items = result.get("recommendations") or []

    # Defensive: if the model didn't return exactly as many items as we
    # gave it, don't trust any of it -- fall back rather than risk a
    # mismatched/garbled list.
    if len(enhanced_items) != len(recommendations):
        logger.warning(
            "Recommendation enhancement returned %d items, expected %d -- "
            "falling back to rule-based recommendations",
            len(enhanced_items),
            len(recommendations),
        )
        return recommendations

    try:
        return [
            RecommendationResponse(
                title=enhanced_items[i].get("title") or original.title,
                description=(
                    enhanced_items[i].get("description") or original.description
                ),
                priority=original.priority,  # priority is never LLM-controlled
            )
            for i, original in enumerate(recommendations)
        ]
    except Exception:
        logger.exception("Failed to merge enhanced recommendations")
        return recommendations
