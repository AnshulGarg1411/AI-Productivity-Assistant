from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum
)

from app.enums.meeting_enum import (
    MeetingType,
    MeetingStatus
)

from app.models.base import Base


class Meeting(Base):

    __tablename__ = "meetings"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # Google Calendar Event ID
    google_event_id = Column(
        String,
        unique=True,
        nullable=True
    )

    title = Column(
        String,
        nullable=False
    )

    description = Column(
        String,
        nullable=True
    )

    organizer = Column(
        String,
        nullable=True
    )

    location = Column(
        String,
        nullable=True
    )

    meeting_link = Column(
        String,
        nullable=True
    )

    # Store attendee emails separated by commas
    attendees = Column(
        String,
        nullable=True
    )

    start_time = Column(
        DateTime,
        nullable=False
    )

    end_time = Column(
        DateTime,
        nullable=False
    )

    meeting_type = Column(
        Enum(MeetingType),
        nullable=False
    )

    status = Column(
        Enum(MeetingStatus),
        nullable=False
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