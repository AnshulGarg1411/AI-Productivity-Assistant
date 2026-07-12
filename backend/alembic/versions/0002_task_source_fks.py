"""tasks: replace free-form source_id with typed source_email_id/source_meeting_id

Revision ID: 0002_task_source_fks
Revises: 0001_baseline
Create Date: 2026-07-04

Why: `source_id` was an untyped String with no foreign key, so nothing
guaranteed it actually pointed at a real email/meeting row. This migration
replaces it with two proper nullable FKs (only one of which is ever set,
enforced by a CHECK constraint), so the eventual AI-driven task creation
(see TaskSource.EMAIL / TaskSource.CALENDAR) has real referential integrity
instead of a loose string.

Nothing in the app currently populates source_id with real data (verified:
create_task() is only ever called from the manual POST /tasks/ endpoint), so
this is a safe structural change with no data migration needed.
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_task_source_fks"
down_revision = "0001_baseline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tasks",
        sa.Column(
            "source_email_id",
            sa.Integer,
            sa.ForeignKey("emails.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column(
        "tasks",
        sa.Column(
            "source_meeting_id",
            sa.Integer,
            sa.ForeignKey("meetings.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_tasks_source_email_id", "tasks", ["source_email_id"]
    )
    op.create_index(
        "ix_tasks_source_meeting_id", "tasks", ["source_meeting_id"]
    )

    op.drop_column("tasks", "source_id")

    op.create_check_constraint(
        "ck_task_source_consistency",
        "tasks",
        "(source_email_id IS NULL OR source = 'EMAIL') AND "
        "(source_meeting_id IS NULL OR source = 'CALENDAR') AND "
        "NOT (source_email_id IS NOT NULL AND source_meeting_id IS NOT NULL)",
    )


def downgrade() -> None:
    op.drop_constraint("ck_task_source_consistency", "tasks", type_="check")

    op.add_column("tasks", sa.Column("source_id", sa.String, nullable=True))

    op.drop_index("ix_tasks_source_meeting_id", table_name="tasks")
    op.drop_index("ix_tasks_source_email_id", table_name="tasks")
    op.drop_column("tasks", "source_meeting_id")
    op.drop_column("tasks", "source_email_id")
