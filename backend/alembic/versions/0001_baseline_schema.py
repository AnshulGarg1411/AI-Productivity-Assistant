"""baseline schema (matches pre-Alembic create_all state)

Revision ID: 0001_baseline
Revises:
Create Date: 2026-07-04

This migration intentionally mirrors the schema that Base.metadata.create_all()
was already producing before Alembic was introduced. If your database already
has these tables (from running the app before this migration existed), do NOT
run `alembic upgrade head` directly -- run:

    alembic stamp 0001_baseline

first, to tell Alembic "the DB is already at this point," then
`alembic upgrade head` will only apply what comes after (the 0002 migration).

For a brand new/empty database, `alembic upgrade head` runs both migrations
and builds everything from scratch -- no stamping needed.
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("email", sa.String, nullable=False, unique=True),
    )

    op.create_table(
        "google_accounts",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id"),
            nullable=False,
            unique=True,
        ),
        sa.Column("google_email", sa.String, nullable=False, unique=True),
        sa.Column("access_token", sa.Text, nullable=False),
        sa.Column("refresh_token", sa.Text, nullable=True),
        sa.Column("expires_at", sa.DateTime, nullable=True),
        sa.Column("scope", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    op.create_table(
        "emails",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("gmail_message_id", sa.String, nullable=False, unique=True),
        sa.Column("thread_id", sa.String, nullable=False),
        sa.Column("sender", sa.String, nullable=False),
        sa.Column("subject", sa.String, nullable=False),
        sa.Column("snippet", sa.String, nullable=True),
        sa.Column("body", sa.Text, nullable=True),
        sa.Column("labels", sa.String, nullable=True),
        sa.Column("category", sa.String, nullable=True),
        sa.Column("importance", sa.Boolean, server_default=sa.false()),
        sa.Column("starred", sa.Boolean, server_default=sa.false()),
        sa.Column("unread", sa.Boolean, server_default=sa.true()),
        sa.Column("archived", sa.Boolean, server_default=sa.false()),
        sa.Column("has_attachment", sa.Boolean, server_default=sa.false()),
        sa.Column("received_at", sa.DateTime, nullable=False),
    )

    meeting_type_enum = sa.Enum("ONLINE", "OFFLINE", name="meetingtype")
    meeting_status_enum = sa.Enum(
        "CONFIRMED", "CANCELLED", "TENTATIVE", name="meetingstatus"
    )

    op.create_table(
        "meetings",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("google_event_id", sa.String, nullable=True, unique=True),
        sa.Column("title", sa.String, nullable=False),
        sa.Column("description", sa.String, nullable=True),
        sa.Column("organizer", sa.String, nullable=True),
        sa.Column("location", sa.String, nullable=True),
        sa.Column("meeting_link", sa.String, nullable=True),
        sa.Column("attendees", sa.String, nullable=True),
        sa.Column("start_time", sa.DateTime, nullable=False),
        sa.Column("end_time", sa.DateTime, nullable=False),
        sa.Column("meeting_type", meeting_type_enum, nullable=False),
        sa.Column("status", meeting_status_enum, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    task_priority_enum = sa.Enum("LOW", "MEDIUM", "HIGH", name="taskpriority")
    task_status_enum = sa.Enum(
        "TODO", "IN_PROGRESS", "COMPLETED", name="taskstatus"
    )
    task_category_enum = sa.Enum(
        "WORK", "STUDY", "PERSONAL", "HEALTH", name="taskcategory"
    )
    task_source_enum = sa.Enum(
        "MANUAL", "EMAIL", "CALENDAR", "AI", name="tasksource"
    )

    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column(
            "user_id", sa.Integer, sa.ForeignKey("users.id"),
            nullable=False, index=True
        ),
        sa.Column("title", sa.String, nullable=False),
        sa.Column("description", sa.String, nullable=True),
        sa.Column(
            "source", task_source_enum, nullable=False,
            server_default="MANUAL"
        ),
        # Original (pre-refactor) free-form source reference.
        # Replaced by typed FKs in migration 0002.
        sa.Column("source_id", sa.String, nullable=True),
        sa.Column("category", task_category_enum, nullable=False),
        sa.Column("priority", task_priority_enum, nullable=False),
        sa.Column(
            "status", task_status_enum, nullable=False,
            server_default="TODO"
        ),
        sa.Column("due_date", sa.DateTime, nullable=False),
        sa.Column("estimated_minutes", sa.Integer, nullable=False),
        sa.Column("actual_minutes", sa.Integer, nullable=True),
        sa.Column("energy_level", sa.Integer, nullable=True),
        sa.Column("is_recurring", sa.Boolean, server_default=sa.false()),
        sa.Column("completed_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("tasks")
    op.drop_table("meetings")
    op.drop_table("emails")
    op.drop_table("google_accounts")
    op.drop_table("users")

    sa.Enum(name="tasksource").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="taskcategory").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="taskstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="taskpriority").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="meetingstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="meetingtype").drop(op.get_bind(), checkfirst=True)
