"""
Tests for app/ai/recommendation_agent.py. The critical safety property:
priority is never LLM-controlled, and a count mismatch from the model
causes a full fallback rather than a partially-trusted merge.
"""
import pytest

from app.ai import recommendation_agent as agent
from app.core.config import settings
from app.schemas.dashboard_schema import RecommendationResponse


@pytest.fixture()
def recommendations():
    return [
        RecommendationResponse(
            title="Reply to Important Emails",
            description="You have 3 important unread emails.",
            priority="HIGH",
        ),
        RecommendationResponse(
            title="Take a Break",
            description="You've been working for 3 hours straight.",
            priority="LOW",
        ),
    ]


class TestAIFeaturesDisabled:
    def test_returns_unchanged_when_disabled(self, recommendations, monkeypatch):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", False)

        result = agent.enhance_recommendations(recommendations)

        assert result == recommendations


class TestEmptyInput:
    def test_returns_empty_list_unchanged(self, monkeypatch):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)

        result = agent.enhance_recommendations([])

        assert result == []


class TestGeminiFailureFallback:
    def test_falls_back_when_generate_json_returns_none(
        self, recommendations, monkeypatch
    ):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)
        monkeypatch.setattr(agent, "generate_json", lambda *a, **k: None)

        result = agent.enhance_recommendations(recommendations)

        assert result == recommendations


class TestCountMismatchSafety:
    def test_falls_back_when_llm_returns_wrong_number_of_items(
        self, recommendations, monkeypatch
    ):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)
        monkeypatch.setattr(
            agent,
            "generate_json",
            lambda *a, **k: {
                "recommendations": [
                    {"title": "Only one item", "description": "x"}
                ]
            },
        )

        result = agent.enhance_recommendations(recommendations)

        # 1 returned vs 2 expected -- must discard and fall back entirely
        assert result == recommendations


class TestSuccessfulEnhancement:
    def test_rewrites_title_and_description_but_never_priority(
        self, recommendations, monkeypatch
    ):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)
        monkeypatch.setattr(
            agent,
            "generate_json",
            lambda *a, **k: {
                "recommendations": [
                    {
                        "title": "Clear those 3 urgent emails first",
                        "description": "Sarah and two others are waiting on replies.",
                    },
                    {
                        "title": "Step away for 10 minutes",
                        "description": "A short break now will help you refocus.",
                    },
                ]
            },
        )

        result = agent.enhance_recommendations(recommendations)

        assert result[0].title == "Clear those 3 urgent emails first"
        assert result[0].priority == "HIGH"  # unchanged, never LLM-controlled
        assert result[1].title == "Step away for 10 minutes"
        assert result[1].priority == "LOW"  # unchanged

    def test_preserves_order(self, recommendations, monkeypatch):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)
        monkeypatch.setattr(
            agent,
            "generate_json",
            lambda *a, **k: {
                "recommendations": [
                    {"title": "First rewritten", "description": "d1"},
                    {"title": "Second rewritten", "description": "d2"},
                ]
            },
        )

        result = agent.enhance_recommendations(recommendations)

        assert [r.title for r in result] == ["First rewritten", "Second rewritten"]
