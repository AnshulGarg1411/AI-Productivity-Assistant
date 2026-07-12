from datetime import datetime
from typing import List

from pydantic import BaseModel

from app.enums.meeting_enum import (
    MeetingType,
    MeetingStatus
)


# ======================================================
# CRUD Schemas
# ======================================================

class MeetingCreate(BaseModel):

    user_id: int

    google_event_id: str | None = None

    title: str

    description: str | None = None

    organizer: str | None = None

    location: str | None = None

    meeting_link: str | None = None

    attendees: str | None = None

    start_time: datetime

    end_time: datetime

    meeting_type: MeetingType

    status: MeetingStatus


class MeetingResponse(MeetingCreate):

    id: int

    created_at: datetime

    updated_at: datetime

    class Config:

        from_attributes = True


# ======================================================
# Meeting Hours
# ======================================================

class MeetingHoursResponse(BaseModel):

    meeting_hours: float


# ======================================================
# Conflict Schema
# ======================================================

class ConflictResponse(BaseModel):

    meeting1: str

    meeting2: str


# ======================================================
# Free Slot Schema
# ======================================================

class FreeSlotResponse(BaseModel):

    start: datetime

    end: datetime

    duration_minutes: int


# ======================================================
# Focus Window Schema
# ======================================================

class FocusWindowResponse(BaseModel):

    start: datetime

    end: datetime

    duration_minutes: int


# ======================================================
# Analytics Schema
# ======================================================

class MeetingAnalyticsResponse(BaseModel):

    meeting_hours: float

    meeting_load: str

    total_meetings: int

    conflicts: List[ConflictResponse]

    free_slots: List[FreeSlotResponse]

    best_focus_window: FocusWindowResponse | None = None


# ======================================================
# Calendar Sync Response
# ======================================================

class CalendarSyncResponse(BaseModel):

    synced: int

    skipped: int

    total: int

# ======================================================
# Dashboard Meeting Card
# ======================================================

class MeetingCardResponse(BaseModel):

    title: str

    start: str

    end: str

    meeting_type: MeetingType

    location: str | None = None

    class Config:
        from_attributes = True


# ======================================================
# Dashboard Schedule
# ======================================================

class TodayScheduleResponse(BaseModel):

    meetings: list[MeetingCardResponse]