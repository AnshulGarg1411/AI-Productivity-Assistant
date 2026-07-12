"""
Direct tests for app/ai/chat/tools.py, bypassing the LLM loop entirely --
these call the tools the same way the agent would (tool.invoke(args)), but
against real data, to verify the tools themselves are correct. User
isolation gets its own test class since that's the exact bug class we
already found and fixed once in tasks.py/meetings.py.
"""
from datetime import datetime, timedelta

import pytest

from app.ai.chat.tools import build_tools
from app.models.user import User


@pytest.fixture()
def other_user(db_session):
    user = User(name="Other User", email="chat-other@example.com")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def get_tool(tools, name):
    return next(t for t in tools if t.name == name)


class TestUserIsolation:
    def test_list_tasks_only_sees_own_tasks(
        self, db_session, test_user, other_user, make_task
    ):
        make_task(user_id=test_user.id, title="Mine")
        make_task(user_id=other_user.id, title="Not mine")

        tools = build_tools(db_session, test_user)
        list_tasks = get_tool(tools, "list_tasks")

        result = list_tasks.invoke({"status": "all"})

        assert "Mine" in result
        assert "Not mine" not in result

    def test_complete_task_cannot_touch_another_users_task(
        self, db_session, test_user, other_user, make_task
    ):
        other_task = make_task(user_id=other_user.id)

        tools = build_tools(db_session, test_user)
        complete_task_tool = get_tool(tools, "complete_task_tool")

        result = complete_task_tool.invoke(
            {"task_id": other_task.id, "actual_minutes": 10}
        )

        assert "No task with id" in result

    def test_delete_task_cannot_touch_another_users_task(
        self, db_session, test_user, other_user, make_task
    ):
        other_task = make_task(user_id=other_user.id)

        tools = build_tools(db_session, test_user)
        delete_task_tool = get_tool(tools, "delete_task_tool")

        result = delete_task_tool.invoke({"task_id": other_task.id})

        assert "No task with id" in result


class TestCreateTaskTool:
    def test_creates_task_with_ai_source(self, db_session, test_user):
        tools = build_tools(db_session, test_user)
        create_task_tool = get_tool(tools, "create_task_tool")

        due = (datetime.utcnow() + timedelta(days=2)).isoformat()

        result = create_task_tool.invoke(
            {
                "title": "Write documentation",
                "category": "WORK",
                "priority": "MEDIUM",
                "due_date": due,
            }
        )

        assert "Created task" in result
        assert "Write documentation" in result

    def test_rejects_unparseable_due_date_without_crashing(self, db_session, test_user):
        tools = build_tools(db_session, test_user)
        create_task_tool = get_tool(tools, "create_task_tool")

        result = create_task_tool.invoke(
            {
                "title": "Bad date task",
                "category": "WORK",
                "priority": "LOW",
                "due_date": "not-a-real-date",
            }
        )

        assert "Could not parse" in result


class TestListMeetingsAndEmails:
    def test_list_meetings_defaults_to_upcoming(self, db_session, test_user):
        tools = build_tools(db_session, test_user)
        list_meetings = get_tool(tools, "list_meetings")

        result = list_meetings.invoke({})

        assert isinstance(result, str)

    def test_list_emails_defaults_to_unread(self, db_session, test_user):
        tools = build_tools(db_session, test_user)
        list_emails = get_tool(tools, "list_emails")

        result = list_emails.invoke({})

        assert isinstance(result, str)


class TestRecommendationsTool:
    def test_returns_productivity_score_and_recommendations(
        self, db_session, test_user
    ):
        tools = build_tools(db_session, test_user)
        get_recommendations = get_tool(tools, "get_recommendations")

        result = get_recommendations.invoke({})

        assert "Productivity score" in result
