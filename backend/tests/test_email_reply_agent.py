from datetime import datetime

import pytest

from app.ai import email_reply_agent as agent
from app.core.config import settings
from app.models.email import Email


@pytest.fixture()
def sample_email(db_session, test_user):
    email = Email(
        user_id=test_user.id,
        gmail_message_id="msg-reply-1",
        thread_id="thread-1",
        sender="client@example.com",
        subject="Question about the proposal",
        snippet="Can you clarify the timeline?",
        body="Hi, can you clarify the project timeline in the proposal?",
        received_at=datetime.utcnow(),
    )
    db_session.add(email)
    db_session.commit()
    db_session.refresh(email)
    return email


class TestUnavailability:
    def test_raises_when_ai_disabled(self, sample_email, monkeypatch):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", False)

        with pytest.raises(agent.SmartReplyUnavailable):
            agent.generate_reply(sample_email)


class TestGeneration:
    def test_returns_generated_text(self, sample_email, monkeypatch):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)
        monkeypatch.setattr(
            agent, "generate_text", lambda *a, **k: "  Sure, the timeline is 6 weeks.  "
        )

        result = agent.generate_reply(sample_email, tone="formal")

        assert result == "Sure, the timeline is 6 weeks."

    def test_invalid_tone_falls_back_to_friendly(self, sample_email, monkeypatch):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)

        captured = {}

        def fake_generate_text(prompt, **kwargs):
            captured["prompt"] = prompt
            return "A reply."

        monkeypatch.setattr(agent, "generate_text", fake_generate_text)

        agent.generate_reply(sample_email, tone="angry-shouting")

        assert "friendly" in captured["prompt"].lower()

    def test_raises_when_generation_fails(self, sample_email, monkeypatch):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)
        monkeypatch.setattr(agent, "generate_text", lambda *a, **k: None)

        with pytest.raises(agent.SmartReplyUnavailable):
            agent.generate_reply(sample_email)
