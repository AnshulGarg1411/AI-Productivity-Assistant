"""
Tests for app/ai/chat/agent.py. The chat model itself is always replaced
with a scripted fake (never a real Gemini call) so these tests are fast,
deterministic, and verify the loop logic: tool execution, feeding results
back to the model, and the iteration safety cap.
"""
import pytest
from langchain_core.messages import AIMessage

from app.ai.chat import agent as chat_agent
from app.core.config import settings


class FakeModel:
    """A scripted stand-in for ChatGoogleGenerativeAI.bind_tools(...).
    `responses` is a list of AIMessage objects returned in order, one per
    .invoke() call."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.invocations = 0

    def bind_tools(self, tools):
        return self

    def invoke(self, messages):
        self.invocations += 1
        return self.responses.pop(0)


class TestUnavailability:
    def test_raises_when_ai_disabled(self, db_session, test_user, monkeypatch):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", False)

        with pytest.raises(chat_agent.ChatAgentUnavailable):
            chat_agent.run_chat_agent(db_session, test_user, "hello")


class TestToolCallingLoop:
    def test_direct_answer_with_no_tool_calls(
        self, db_session, test_user, monkeypatch
    ):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)

        fake = FakeModel([AIMessage(content="Hello! How can I help?", tool_calls=[])])
        monkeypatch.setattr(chat_agent, "_get_model", lambda: fake)

        result = chat_agent.run_chat_agent(db_session, test_user, "hi")

        assert result["reply"] == "Hello! How can I help?"
        assert result["tool_calls"] == []
        assert fake.invocations == 1

    def test_executes_a_real_tool_and_returns_final_answer(
        self, db_session, test_user, monkeypatch
    ):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)

        # Turn 1: model asks to call list_tasks. Turn 2: model gives a final answer.
        fake = FakeModel(
            [
                AIMessage(
                    content="",
                    tool_calls=[
                        {"name": "list_tasks", "args": {"status": "all"}, "id": "call_1"}
                    ],
                ),
                AIMessage(content="You have no tasks right now.", tool_calls=[]),
            ]
        )
        monkeypatch.setattr(chat_agent, "_get_model", lambda: fake)

        result = chat_agent.run_chat_agent(
            db_session, test_user, "what are my tasks?"
        )

        assert result["reply"] == "You have no tasks right now."
        assert result["tool_calls"] == ["list_tasks"]
        assert fake.invocations == 2

    def test_creates_a_real_task_via_tool_call(
        self, db_session, test_user, monkeypatch
    ):
        from datetime import datetime, timedelta
        from app.models.task import Task

        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)

        due = (datetime.utcnow() + timedelta(days=1)).isoformat()

        fake = FakeModel(
            [
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": "create_task_tool",
                            "args": {
                                "title": "Buy groceries",
                                "category": "PERSONAL",
                                "priority": "LOW",
                                "due_date": due,
                            },
                            "id": "call_1",
                        }
                    ],
                ),
                AIMessage(content="Done, I've created that task.", tool_calls=[]),
            ]
        )
        monkeypatch.setattr(chat_agent, "_get_model", lambda: fake)

        result = chat_agent.run_chat_agent(
            db_session, test_user, "add a task to buy groceries"
        )

        assert result["tool_calls"] == ["create_task_tool"]

        created = (
            db_session.query(Task)
            .filter(Task.title == "Buy groceries", Task.user_id == test_user.id)
            .first()
        )
        assert created is not None
        assert created.source.value == "AI"

    def test_unknown_tool_name_does_not_crash_the_loop(
        self, db_session, test_user, monkeypatch
    ):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)

        fake = FakeModel(
            [
                AIMessage(
                    content="",
                    tool_calls=[
                        {"name": "not_a_real_tool", "args": {}, "id": "call_1"}
                    ],
                ),
                AIMessage(content="Sorry, I couldn't do that.", tool_calls=[]),
            ]
        )
        monkeypatch.setattr(chat_agent, "_get_model", lambda: fake)

        result = chat_agent.run_chat_agent(db_session, test_user, "do something weird")

        assert result["reply"] == "Sorry, I couldn't do that."

    def test_stops_at_iteration_cap_instead_of_looping_forever(
        self, db_session, test_user, monkeypatch
    ):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)

        # The model NEVER stops asking for tool calls -- the loop must
        # bail out rather than spin forever.
        infinite_tool_calls = AIMessage(
            content="",
            tool_calls=[{"name": "list_tasks", "args": {}, "id": "call_x"}],
        )
        fake = FakeModel([infinite_tool_calls] * 10)
        monkeypatch.setattr(chat_agent, "_get_model", lambda: fake)

        result = chat_agent.run_chat_agent(db_session, test_user, "loop forever")

        assert fake.invocations == chat_agent.MAX_TOOL_ITERATIONS
        assert "wasn't able to finish" in result["reply"]

    def test_tool_exception_is_caught_and_fed_back_as_error_message(
        self, db_session, test_user, monkeypatch
    ):
        monkeypatch.setattr(settings, "AI_FEATURES_ENABLED", True)

        fake = FakeModel(
            [
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": "create_task_tool",
                            # Missing required args on purpose to trigger a failure
                            "args": {"title": "x"},
                            "id": "call_1",
                        }
                    ],
                ),
                AIMessage(content="Something went wrong creating that task.", tool_calls=[]),
            ]
        )
        monkeypatch.setattr(chat_agent, "_get_model", lambda: fake)

        # Should not raise -- the agent loop catches tool failures
        result = chat_agent.run_chat_agent(db_session, test_user, "make a bad task")

        assert result["reply"] == "Something went wrong creating that task."
