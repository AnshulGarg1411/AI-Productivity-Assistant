"""
Tests for app/ai/task_extraction_agent.py. Gemini itself is always mocked
(via monkeypatching generate_json) -- these tests never hit the network,
they verify the surrounding logic: the AI-disabled fallback, duplicate
prevention, and correct mapping of a (mocked) LLM response into a real Task.
"""
from datetime import datetime, timedelta

import pytest

from app.ai import task_extraction_agent as agent
from app.core.config import settings
from app.models.email import Email
from app.models.meeting import Meeting
from app.models.task import Task


@pytest.fixture()
def sample_email(db_session, test_user):
    email = Email(
        user_id=test_user.id,
        gmail_message_id="msg-1",
        thread_id="thread-1",
        sender="prof@university.edu",
        subject="Assignment due Friday",
        snippet="Please submit the assignment by Friday.",
        body="Please submit the assignment by Friday at 5pm.",
        received_at=datetime.utcnow(),
    )
    db_session.add(email)
    db_session.commit()
    db_session.refresh(email)
    return email


@pytest.fixture()
def sample_meeting(db_session, test_user):
    meeting = Meeting(
        user_id=test_user.id,
        title="Sprint planning",
        description="Bring your updated task estimates.",
        start_time=datetime.utcnow() + timedelta(days=1),
        end_time=datetime.utcnow() + timedelta(days=1, hours=1),
        meeting_type="ONLINE",
        status="CONFIRMED",
    )
    db_session.add(meeting)
    db_session.commit()
    db_session.refresh(meeting)
    return meeting


class TestAIFeaturesDisabled:
    """When there's no Gemini key, nothing here should ever call the network
    or create a task -- it should just quietly do nothing."""

    def test_email_extraction_noop_when_disabled(
        self, db_session, sample_email, monkeypatch
    ):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", False)

        result = agent.create_task_from_email(db_session, sample_email)

        assert result is None

    def test_meeting_extraction_noop_when_disabled(
        self, db_session, sample_meeting, monkeypatch
    ):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", False)

        result = agent.create_task_from_meeting(db_session, sample_meeting)

        assert result is None


class TestDuplicatePrevention:
    def test_skips_email_that_already_has_a_task(
        self, db_session, sample_email, test_user, monkeypatch
    ):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)

        existing = Task(
            user_id=test_user.id,
            title="Already extracted",
            category="WORK",
            priority="MEDIUM",
            status="TODO",
            due_date=datetime.utcnow() + timedelta(days=1),
            estimated_minutes=30,
            source="EMAIL",
            source_email_id=sample_email.id,
        )
        db_session.add(existing)
        db_session.commit()

        called = {"count": 0}

        def fake_generate_json(*args, **kwargs):
            called["count"] += 1
            return {"has_task": True, "title": "x", "priority": "LOW", "category": "WORK"}

        monkeypatch.setattr(agent, "generate_json", fake_generate_json)

        result = agent.create_task_from_email(db_session, sample_email)

        assert result is None
        assert called["count"] == 0  # never even called the LLM


class TestEmailTaskExtraction:
    def test_creates_task_when_llm_finds_one(
        self, db_session, sample_email, monkeypatch
    ):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)
        monkeypatch.setattr(
            agent,
            "generate_json",
            lambda *a, **k: {
                "has_task": True,
                "title": "Submit assignment",
                "due_date": "",
                "priority": "HIGH",
                "category": "STUDY",
            },
        )

        task = agent.create_task_from_email(db_session, sample_email)

        assert task is not None
        assert task.title == "Submit assignment"
        assert task.priority.value == "HIGH"
        assert task.category.value == "STUDY"
        assert task.source.value == "EMAIL"
        assert task.source_email_id == sample_email.id
        assert task.source_meeting_id is None

    def test_no_task_created_when_llm_says_no(
        self, db_session, sample_email, monkeypatch
    ):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)
        monkeypatch.setattr(
            agent,
            "generate_json",
            lambda *a, **k: {"has_task": False, "title": "", "priority": "LOW", "category": "WORK"},
        )

        task = agent.create_task_from_email(db_session, sample_email)

        assert task is None

    def test_falls_back_gracefully_when_gemini_call_fails(
        self, db_session, sample_email, monkeypatch
    ):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)
        monkeypatch.setattr(agent, "generate_json", lambda *a, **k: None)

        task = agent.create_task_from_email(db_session, sample_email)

        assert task is None

    def test_invalid_priority_from_llm_falls_back_to_medium(
        self, db_session, sample_email, monkeypatch
    ):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)
        monkeypatch.setattr(
            agent,
            "generate_json",
            lambda *a, **k: {
                "has_task": True,
                "title": "Something",
                "priority": "URGENT!!",  # not a real enum value
                "category": "NOT_A_CATEGORY",
            },
        )

        task = agent.create_task_from_email(db_session, sample_email)

        assert task.priority.value == "MEDIUM"
        assert task.category.value == "WORK"

    def test_due_date_falls_back_when_llm_gives_none(
        self, db_session, sample_email, monkeypatch
    ):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)
        monkeypatch.setattr(
            agent,
            "generate_json",
            lambda *a, **k: {
                "has_task": True,
                "title": "Something",
                "due_date": "",
                "priority": "LOW",
                "category": "WORK",
            },
        )

        task = agent.create_task_from_email(db_session, sample_email)

        # fallback is received_at + 2 days
        expected = sample_email.received_at + timedelta(days=2)
        assert abs((task.due_date - expected).total_seconds()) < 5


class TestMeetingTaskExtraction:
    def test_creates_task_linked_to_meeting(
        self, db_session, sample_meeting, monkeypatch
    ):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)
        monkeypatch.setattr(
            agent,
            "generate_json",
            lambda *a, **k: {
                "has_task": True,
                "title": "Prepare task estimates",
                "due_date": "",
                "priority": "MEDIUM",
                "category": "WORK",
            },
        )

        task = agent.create_task_from_meeting(db_session, sample_meeting)

        assert task is not None
        assert task.source.value == "CALENDAR"
        assert task.source_meeting_id == sample_meeting.id
        assert task.source_email_id is None
        # fallback due date is the meeting's start time
        assert task.due_date == sample_meeting.start_time


class TestBatchExtraction:
    def test_batch_extraction_never_raises_even_if_one_item_fails(
        self, db_session, sample_email, monkeypatch
    ):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)

        def blows_up(*a, **k):
            raise RuntimeError("simulated LLM failure")

        monkeypatch.setattr(agent, "generate_json", blows_up)

        # Should not raise -- errors are caught and logged internally
        agent.extract_tasks_from_new_emails(db_session, [sample_email])
