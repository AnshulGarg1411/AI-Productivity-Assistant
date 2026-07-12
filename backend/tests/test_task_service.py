"""
Service-layer tests for app/services/task_service.py, using a real (test)
DB session. These specifically guard against the user-scoping bug we found
and fixed in tasks.py -- every query here asserts that one user can never
see or modify another user's tasks.
"""
from datetime import datetime, timedelta

import pytest

from app.services import task_service
from app.models.user import User


@pytest.fixture()
def other_user(db_session):
    user = User(name="Other User", email="other@example.com")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestUserIsolation:
    """The exact bug class we found in the original tasks.py router --
    pin it down at the service layer so it can't silently regress."""

    def test_get_all_tasks_only_returns_own_tasks(
        self, db_session, test_user, other_user, make_task
    ):
        make_task(user_id=test_user.id, title="Mine")
        make_task(user_id=other_user.id, title="Not mine")

        result = task_service.get_all_tasks(db_session, test_user.id)

        assert len(result) == 1
        assert result[0].title == "Mine"

    def test_get_task_by_id_cannot_fetch_other_users_task(
        self, db_session, test_user, other_user, make_task
    ):
        other_task = make_task(user_id=other_user.id)

        result = task_service.get_task_by_id(
            db_session, test_user.id, other_task.id
        )

        assert result is None

    def test_delete_task_cannot_delete_other_users_task(
        self, db_session, test_user, other_user, make_task
    ):
        other_task = make_task(user_id=other_user.id)

        deleted = task_service.delete_task(
            db_session, test_user.id, other_task.id
        )

        assert deleted is False
        # and it's still there
        assert (
            task_service.get_task_by_id(
                db_session, other_user.id, other_task.id
            )
            is not None
        )


class TestTaskLifecycle:
    def test_create_then_complete_task(self, db_session, test_user):
        task = task_service.create_task(
            db_session,
            {
                "user_id": test_user.id,
                "title": "Ship the feature",
                "category": "WORK",
                "priority": "HIGH",
                "due_date": datetime.utcnow() + timedelta(days=1),
                "estimated_minutes": 60,
            },
        )

        assert task.status.value == "TODO"

        completed = task_service.complete_task(
            db_session, test_user.id, task.id, actual_minutes=75
        )

        assert completed.status.value == "COMPLETED"
        assert completed.actual_minutes == 75
        assert completed.completed_at is not None

    def test_complete_nonexistent_task_returns_none(self, db_session, test_user):
        result = task_service.complete_task(
            db_session, test_user.id, task_id=9999, actual_minutes=10
        )
        assert result is None

    def test_pending_tasks_excludes_completed(
        self, db_session, test_user, make_task
    ):
        make_task(user_id=test_user.id, status="TODO")
        make_task(user_id=test_user.id, status="COMPLETED")

        pending = task_service.get_pending_tasks(db_session, test_user.id)

        assert len(pending) == 1
        assert pending[0].status.value == "TODO"

    def test_overdue_tasks_only_returns_past_due_incomplete(
        self, db_session, test_user, make_task
    ):
        make_task(
            user_id=test_user.id,
            due_date=datetime.utcnow() - timedelta(days=2),
            status="TODO",
        )
        make_task(
            user_id=test_user.id,
            due_date=datetime.utcnow() + timedelta(days=2),
            status="TODO",
        )

        overdue = task_service.get_overdue_tasks(db_session, test_user.id)

        assert len(overdue) == 1


class TestTaskAnalytics:
    def test_analytics_reflects_actual_task_data(
        self, db_session, test_user, make_task
    ):
        make_task(user_id=test_user.id, status="COMPLETED", actual_minutes=30)
        make_task(user_id=test_user.id, status="TODO")

        analytics = task_service.get_task_analytics(db_session, test_user.id)

        assert analytics["total_tasks"] == 2
        assert analytics["completed_tasks"] == 1
        assert analytics["pending_tasks"] == 1
