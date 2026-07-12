from typing import List

from pydantic import BaseModel
from app.schemas.email_schema import (
    EmailCardResponse
)
from app.schemas.meeting_schema import (
    MeetingCardResponse
)
from app.schemas.task_schema import (
    TaskCardResponse,
     DeadlineCardResponse
)
from app.schemas.morning_brief_schema import MorningBriefResponse
# ======================================================
# USER
# ======================================================

class UserDashboardResponse(BaseModel):

    id: int

    name: str

    email: str


# ======================================================
# EMAIL SUMMARY
# ======================================================

class EmailDashboardResponse(BaseModel):

    total: int

    unread: int

    important: int


# ======================================================
# MEETING SUMMARY
# ======================================================

class MeetingDashboardResponse(BaseModel):

    today: int

    upcoming: int

    meeting_hours: float


# ======================================================
# TASK SUMMARY
# ======================================================

class TaskDashboardResponse(BaseModel):

    pending: int

    completed: int

    overdue: int

    high_priority: int


# ======================================================
# FOCUS WINDOW
# ======================================================

class FocusWindowDashboardResponse(BaseModel):

    start: str

    end: str

    duration_minutes: int


# ======================================================
# PRODUCTIVITY
# ======================================================

class ProductivityResponse(BaseModel):

    score: int

    status: str


# ======================================================
# RECOMMENDATION
# ======================================================

class RecommendationResponse(BaseModel):

    title: str

    description: str

    priority: str


# ======================================================
# COMPLETE DASHBOARD
# ======================================================

class DashboardResponse(BaseModel):

    user: UserDashboardResponse

    emails: EmailDashboardResponse

    urgent_emails: list[EmailCardResponse]

    meetings: MeetingDashboardResponse

    tasks: TaskDashboardResponse

    upcoming_deadlines: list[DeadlineCardResponse]

    today_schedule: list[MeetingCardResponse]

    today_tasks: list[TaskCardResponse]

    focus: FocusWindowDashboardResponse | None = None

    productivity: ProductivityResponse

    recommendations: List[RecommendationResponse]

    morning_brief: MorningBriefResponse