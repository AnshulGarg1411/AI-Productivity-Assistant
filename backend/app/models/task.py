from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    Enum,
    CheckConstraint
)

from app.models.base import Base

from app.enums.task_enum import (
    TaskPriority,
    TaskStatus,
    TaskCategory
)

from app.enums.task_enum import (
    TaskSource
)


class Task(Base):

    __tablename__ = "tasks"

    __table_args__ = (
        # A task can be linked to at most one origin record, and only when
        # its source actually is that type. Keeps source/source_*_id from
        # drifting out of sync with each other at the database level.
        CheckConstraint(
            "(source_email_id IS NULL OR source = 'EMAIL') AND "
            "(source_meeting_id IS NULL OR source = 'CALENDAR') AND "
            "NOT (source_email_id IS NOT NULL AND source_meeting_id IS NOT NULL)",
            name="ck_task_source_consistency"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    title = Column(
        String,
        nullable=False
    )

    description = Column(
        String,
        nullable=True
    )

    # ===============================
    # Source Information
    # ===============================
    #
    # `source` records *why* a task exists (typed into the app, extracted
    # from an email, derived from a calendar event, or suggested by AI).
    # When source is EMAIL/CALENDAR, exactly one of the two FKs below points
    # back at the record that generated this task -- this is what lets the
    # AI layer say "this task came from that email" and navigate back to it.
    # Nothing currently populates these except MANUAL creation; they're the
    # intended hook point for future email/calendar-driven task creation.

    source = Column(
        Enum(TaskSource),
        nullable=False,
        default=TaskSource.MANUAL
    )

    source_email_id = Column(
        Integer,
        ForeignKey("emails.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    source_meeting_id = Column(
        Integer,
        ForeignKey("meetings.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # ===============================
    # Task Details
    # ===============================

    category = Column(
        Enum(TaskCategory),
        nullable=False
    )

    priority = Column(
        Enum(TaskPriority),
        nullable=False
    )

    status = Column(
        Enum(TaskStatus),
        nullable=False,
        default=TaskStatus.TODO
    )

    due_date = Column(
        DateTime,
        nullable=False
    )

    estimated_minutes = Column(
        Integer,
        nullable=False
    )

    actual_minutes = Column(
        Integer,
        nullable=True
    )

    energy_level = Column(
        Integer,
        nullable=True
    )

    is_recurring = Column(
        Boolean,
        default=False
    )

    # ===============================
    # Audit Fields
    # ===============================

    completed_at = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )