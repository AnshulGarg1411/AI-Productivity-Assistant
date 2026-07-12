"""
Tests for app/ai/email_intelligence_agent.py. Gemini is always mocked --
these verify the surrounding logic: the AI-disabled fallback, idempotency
(don't re-analyze/re-spend a call on an already-analyzed email), and
correct field updates when analysis succeeds.
"""
from datetime import datetime

import pytest

from app.ai import email_intelligence_agent as agent
from app.core.config import settings
from app.models.email import Email


@pytest.fixture()
def sample_email(db_session, test_user):
    email = Email(
        user_id=test_user.id,
        gmail_message_id="msg-analyze-1",
        thread_id="thread-1",
        sender="hr@company.com",
        subject="Your interview is confirmed",
        snippet="Your interview is scheduled for Monday at 10am.",
        body="Your interview is scheduled for Monday at 10am. Please confirm.",
        category="PROMOTIONS",  # simulating the Gmail-label-derived placeholder
        received_at=datetime.utcnow(),
    )
    db_session.add(email)
    db_session.commit()
    db_session.refresh(email)
    return email


class TestAIFeaturesDisabled:
    def test_noop_when_disabled(self, db_session, sample_email, monkeypatch):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", False)

        result = agent.analyze_email(db_session, sample_email)

        assert result is False
        assert sample_email.ai_summary is None


class TestIdempotency:
    def test_skips_already_analyzed_email(self, db_session, sample_email, monkeypatch):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)
        sample_email.ai_summary = "Already analyzed."
        db_session.commit()

        called = {"count": 0}

        def fake_generate_json(*a, **k):
            called["count"] += 1
            return {"summary": "x", "category": "WORK", "priority": "LOW"}

        monkeypatch.setattr(agent, "generate_json", fake_generate_json)

        result = agent.analyze_email(db_session, sample_email)

        assert result is False
        assert called["count"] == 0


class TestSuccessfulAnalysis:
    def test_updates_summary_category_and_priority(
        self, db_session, sample_email, monkeypatch
    ):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)
        monkeypatch.setattr(
            agent,
            "generate_json",
            lambda *a, **k: {
                "summary": "HR confirms your interview is Monday at 10am.",
                "category": "WORK",
                "priority": "HIGH",
            },
        )

        result = agent.analyze_email(db_session, sample_email)

        assert result is True
        assert sample_email.ai_summary == "HR confirms your interview is Monday at 10am."
        assert sample_email.category == "WORK"
        assert sample_email.ai_priority == "HIGH"

    def test_invalid_category_from_llm_keeps_previous_category(
        self, db_session, sample_email, monkeypatch
    ):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)
        monkeypatch.setattr(
            agent,
            "generate_json",
            lambda *a, **k: {
                "summary": "Some summary.",
                "category": "NOT_A_REAL_CATEGORY",
                "priority": "HIGH",
            },
        )

        agent.analyze_email(db_session, sample_email)

        # falls back to whatever was already there (the Gmail-label guess)
        assert sample_email.category == "PROMOTIONS"

    def test_invalid_priority_from_llm_becomes_none(
        self, db_session, sample_email, monkeypatch
    ):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)
        monkeypatch.setattr(
            agent,
            "generate_json",
            lambda *a, **k: {
                "summary": "Some summary.",
                "category": "WORK",
                "priority": "SUPER URGENT",
            },
        )

        agent.analyze_email(db_session, sample_email)

        assert sample_email.ai_priority is None


class TestGeminiFailureFallback:
    def test_returns_false_when_generate_json_fails(
        self, db_session, sample_email, monkeypatch
    ):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)
        monkeypatch.setattr(agent, "generate_json", lambda *a, **k: None)

        result = agent.analyze_email(db_session, sample_email)

        assert result is False
        assert sample_email.ai_summary is None


class TestBatchAnalysis:
    def test_batch_never_raises_even_if_one_item_fails(
        self, db_session, sample_email, monkeypatch
    ):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)

        def blows_up(*a, **k):
            raise RuntimeError("simulated failure")

        monkeypatch.setattr(agent, "generate_json", blows_up)

        agent.analyze_new_emails(db_session, [sample_email])
