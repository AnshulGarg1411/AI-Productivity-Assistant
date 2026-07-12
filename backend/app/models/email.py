from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text
)

from app.models.base import Base


class Email(Base):

    __tablename__ = "emails"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =====================================================
    # USER
    # =====================================================

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # =====================================================
    # GMAIL IDS
    # =====================================================

    gmail_message_id = Column(
        String,
        unique=True,
        nullable=False
    )

    thread_id = Column(
        String,
        nullable=False
    )

    # =====================================================
    # EMAIL DETAILS
    # =====================================================

    sender = Column(
        String,
        nullable=False
    )

    subject = Column(
        String,
        nullable=False
    )

    snippet = Column(
        String,
        nullable=True
    )

    # Full email body
    body = Column(
        Text,
        nullable=True
    )

    labels = Column(
        String,
        nullable=True
    )

    # category is AI-predicted (WORK/COLLEGE/FINANCE/SHOPPING/TRAVEL/SOCIAL/
    # OTHER) when a Gemini key is configured. Without one, it falls back to
    # a rough guess derived from the Gmail label at sync time (see
    # gmail_service.py) so the field is never left completely empty.
    category = Column(
        String,
        nullable=True
    )

    # AI-generated fields (email_intelligence_agent). Null until/unless
    # AI features are enabled -- the app must work fully without them.
    ai_summary = Column(
        Text,
        nullable=True
    )

    ai_priority = Column(
        String,
        nullable=True
    )

    # =====================================================
    # FLAGS
    # =====================================================

    importance = Column(
        Boolean,
        default=False
    )

    starred = Column(
        Boolean,
        default=False
    )

    unread = Column(
        Boolean,
        default=True
    )

    archived = Column(
        Boolean,
        default=False
    )

    has_attachment = Column(
        Boolean,
        default=False
    )

    # =====================================================
    # RECEIVED TIME
    # =====================================================

    received_at = Column(
        DateTime,
        nullable=False
    )