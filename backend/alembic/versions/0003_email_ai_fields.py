"""emails: add ai_summary and ai_priority columns

Revision ID: 0003_email_ai_fields
Revises: 0002_task_source_fks
Create Date: 2026-07-05

Adds two nullable columns for the email intelligence agent
(summary + HIGH/MEDIUM/LOW priority classification). category already
existed and is now AI-populated where a Gemini key is configured, so it
needs no schema change -- see gmail_service.py / email_intelligence_agent.py.
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_email_ai_fields"
down_revision = "0002_task_source_fks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "emails",
        sa.Column("ai_summary", sa.Text, nullable=True),
    )
    op.add_column(
        "emails",
        sa.Column("ai_priority", sa.String, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("emails", "ai_priority")
    op.drop_column("emails", "ai_summary")
