"""
Tests for app/ai/morning_brief_agent.py. Verifies the core safety property:
numbers/facts (productivity_score, top_priority, focus_window) and
recommendations are never altered by this agent -- only greeting/summary
are narrated -- and any Gemini failure falls back to the original
rule-based brief unchanged.
"""
import pytest

from app.ai import morning_brief_agent as agent
from app.core.config import settings


@pytest.fixture()
def rule_based_brief():
    return {
        "greeting": "Good Morning, Anshul!",
        "summary": ["3 unread emails", "2 meetings today", "5 pending tasks"],
        "top_priority": "Submit assignment",
        "focus_window": "14:00 - 16:00",
        "productivity_score": 78,
        "recommendations": ["Reply to important emails", "Take a break"],
    }


class TestAIFeaturesDisabled:
    def test_returns_unchanged_when_disabled(self, rule_based_brief, monkeypatch):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", False)

        result = agent.narrate_brief(rule_based_brief)

        assert result == rule_based_brief


class TestGeminiFailureFallback:
    def test_returns_unchanged_when_generate_json_returns_none(
        self, rule_based_brief, monkeypatch
    ):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)
        monkeypatch.setattr(agent, "generate_json", lambda *a, **k: None)

        result = agent.narrate_brief(rule_based_brief)

        assert result == rule_based_brief


class TestSuccessfulNarration:
    def test_replaces_greeting_and_summary_but_preserves_everything_else(
        self, rule_based_brief, monkeypatch
    ):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)
        monkeypatch.setattr(
            agent,
            "generate_json",
            lambda *a, **k: {
                "greeting": "Morning, Anshul! Ready to tackle the day?",
                "summary": ["You've got 3 unread emails and 2 meetings today"],
            },
        )

        result = agent.narrate_brief(rule_based_brief)

        assert result["greeting"] == "Morning, Anshul! Ready to tackle the day?"
        assert result["summary"] == ["You've got 3 unread emails and 2 meetings today"]

        # These must never be touched by this agent
        assert result["top_priority"] == rule_based_brief["top_priority"]
        assert result["focus_window"] == rule_based_brief["focus_window"]
        assert result["productivity_score"] == rule_based_brief["productivity_score"]
        assert result["recommendations"] == rule_based_brief["recommendations"]

    def test_recommendations_are_never_read_from_the_llm_response(
        self, rule_based_brief, monkeypatch
    ):
        # Even if the LLM response includes a "recommendations" key (e.g. a
        # model that ignores instructions), this agent must not use it --
        # that's recommendation_agent's job, upstream.
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)
        monkeypatch.setattr(
            agent,
            "generate_json",
            lambda *a, **k: {
                "greeting": "Hey!",
                "summary": ["stuff"],
                "recommendations": ["This should be ignored"],
            },
        )

        result = agent.narrate_brief(rule_based_brief)

        assert result["recommendations"] == rule_based_brief["recommendations"]

    def test_partial_llm_response_keeps_original_fields_for_missing_keys(
        self, rule_based_brief, monkeypatch
    ):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)
        monkeypatch.setattr(
            agent,
            "generate_json",
            lambda *a, **k: {"greeting": "Hey Anshul!", "summary": []},
        )

        result = agent.narrate_brief(rule_based_brief)

        assert result["greeting"] == "Hey Anshul!"
        # empty list is falsy, so this should fall back to the original
        assert result["summary"] == rule_based_brief["summary"]
