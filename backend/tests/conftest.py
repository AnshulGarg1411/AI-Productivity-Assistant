"""
Shared pytest fixtures.

Tests run against an isolated in-memory SQLite database, never the real
Postgres dev/prod database. Each test function gets a fresh schema (tables
are created and dropped per-test) so tests can't leak state into each other.

Alembic migrations manage the *real* database's schema; tests intentionally
use create_all() against a scratch SQLite DB instead, since that's simpler
and faster for test isolation and doesn't require a running Postgres server
in CI.
"""
import os
import sys
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Needed before importing app.core.config, which reads it via os.getenv.
os.environ.setdefault("JWT_SECRET", "test-secret-do-not-use-in-prod")
os.environ.setdefault("SESSION_SECRET", "test-session-secret")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test-client-id")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test-client-secret")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from main import app  # noqa: E402
from app.database.database import get_db  # noqa: E402
from app.models.base import Base  # noqa: E402
from app.models.user import User  # noqa: E402
from app.models.task import Task  # noqa: E402
from app.models.meeting import Meeting  # noqa: E402
from app.models.email import Email  # noqa: E402
from app.core.security import create_access_token  # noqa: E402


@pytest.fixture()
def db_session():
    """A fresh in-memory SQLite DB, isolated per test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    """A TestClient wired to use the isolated test DB instead of Postgres."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def test_user(db_session):
    user = User(name="Test User", email="test@example.com")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def auth_headers(test_user):
    token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def make_task(db_session, test_user):
    """Factory for creating a task directly in the DB with sane defaults."""

    def _make(**overrides):
        defaults = dict(
            user_id=test_user.id,
            title="Sample task",
            category="WORK",
            priority="MEDIUM",
            status="TODO",
            due_date=datetime.utcnow() + timedelta(days=1),
            estimated_minutes=30,
        )
        defaults.update(overrides)
        task = Task(**defaults)
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        return task

    return _make
