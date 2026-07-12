import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text
)

from app.models.base import Base


class GoogleAccount(Base):

    __tablename__ = "google_accounts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        unique=True
    )

    google_email = Column(
        String,
        nullable=False,
        unique=True
    )

    access_token = Column(
        Text,
        nullable=False
    )

    refresh_token = Column(
        Text,
        nullable=True
    )

    expires_at = Column(
        DateTime,
        nullable=True
    )

    scope = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.datetime.utcnow
    )