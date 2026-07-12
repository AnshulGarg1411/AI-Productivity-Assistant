from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.enums.task_enum import (
    TaskPriority,
    TaskStatus,
    TaskCategory
)

from app.enums.task_enum import (
    TaskSource
)


# ======================================================
# CREATE TASK
# ======================================================

class TaskCreate(BaseModel):

    user_id: int

    title: str

    description: Optional[str] = None

    category: TaskCategory

    priority: TaskPriority

    status: TaskStatus = TaskStatus.TODO

    due_date: datetime

    estimated_minutes: int = Field(gt=0)

    actual_minutes: Optional[int] = None

    energy_level: Optional[int] = Field(
        default=None,
        ge=1,
        le=5
    )

    is_recurring: bool = False

    source: TaskSource = TaskSource.MANUAL

    source_email_id: Optional[int] = None

    source_meeting_id: Optional[int] = None


# ======================================================
# UPDATE TASK
# ======================================================

class TaskUpdate(BaseModel):

    title: Optional[str] = None

    description: Optional[str] = None

    category: Optional[TaskCategory] = None

    priority: Optional[TaskPriority] = None

    status: Optional[TaskStatus] = None

    due_date: Optional[datetime] = None

    estimated_minutes: Optional[int] = Field(
        default=None,
        gt=0
    )

    actual_minutes: Optional[int] = None

    energy_level: Optional[int] = Field(
        default=None,
        ge=1,
        le=5
    )

    is_recurring: Optional[bool] = None


# ======================================================
# TASK RESPONSE
# ======================================================

class TaskResponse(BaseModel):

    id: int

    user_id: int

    title: str

    description: Optional[str]

    category: TaskCategory

    priority: TaskPriority

    status: TaskStatus

    due_date: datetime

    estimated_minutes: int

    actual_minutes: Optional[int]

    energy_level: Optional[int]

    is_recurring: bool

    source: TaskSource

    source_email_id: Optional[int]

    source_meeting_id: Optional[int]

    created_at: datetime

    updated_at: datetime

    completed_at: Optional[datetime]

    class Config:

        from_attributes = True


# ======================================================
# ESTIMATED VS ACTUAL
# ======================================================

class EstimatedActualResponse(BaseModel):

    estimated: int

    actual: int


# ======================================================
# TASK ANALYTICS
# ======================================================

class TaskAnalyticsResponse(BaseModel):

    total_tasks: int

    completed_tasks: int

    pending_tasks: int

    completion_rate: float

    overdue_tasks: int

    high_priority_pending: int

    average_completion_time: float

    estimated_vs_actual: EstimatedActualResponse

    productivity_score: float

# ======================================================
# Dashboard Task Card
# ======================================================

class TaskCardResponse(BaseModel):

    title: str

    priority: TaskPriority

    status: TaskStatus

    due_date: datetime

    estimated_minutes: int

    class Config:
        from_attributes = True


# ======================================================
# Today's Tasks
# ======================================================

class TodayTasksResponse(BaseModel):

    tasks: list[TaskCardResponse]

# ======================================================
# Upcoming Deadline Card
# ======================================================

class DeadlineCardResponse(BaseModel):

    title: str

    due_date: datetime

    priority: TaskPriority

    class Config:

        from_attributes = True