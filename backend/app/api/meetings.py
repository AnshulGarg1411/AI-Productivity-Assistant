from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.common_schema import ApiResponse
from app.schemas.meeting_schema import (
    MeetingCreate,
    MeetingResponse,
    MeetingAnalyticsResponse,
    ConflictResponse,
    FreeSlotResponse,
    FocusWindowResponse,
    MeetingHoursResponse
)

from app.services.meeting_service import (
    create_meeting,
    get_all_meetings,
    get_meeting_by_id,
    get_today_meetings,
    get_upcoming_meetings,
    total_meeting_hours,
    get_conflicts,
    get_free_slots,
    get_best_focus_window,
    get_meeting_analytics,
)

router = APIRouter(
    prefix="/meetings",
    tags=["Meetings"]
)


# ===========================
# CRUD
# ===========================

@router.get(
    "/",
    response_model=list[MeetingResponse]
)
def fetch_meetings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_all_meetings(db, current_user.id)


@router.post(
    "/",
    response_model=MeetingResponse
)
def add_meeting(
    meeting: MeetingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meeting_data = meeting.model_dump()
    meeting_data["user_id"] = current_user.id

    return create_meeting(
        db,
        meeting_data
    )


# ===========================
# Analytics
# ===========================

@router.get(
    "/today",
    response_model=list[MeetingResponse]
)
def today_meetings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_today_meetings(db, current_user.id)


@router.get(
    "/upcoming",
    response_model=list[MeetingResponse]
)
def upcoming_meetings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_upcoming_meetings(db, current_user.id)


@router.get("/meeting-hours")
def meeting_hours(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    hours = total_meeting_hours(db, current_user.id)

    return ApiResponse(
        success=True,
        message="Meeting hours calculated successfully.",
        data=hours
    )


@router.get(
    "/conflicts",
    response_model=list[ConflictResponse]
)
def conflicts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_conflicts(db, current_user.id)


@router.get(
    "/free-slots",
    response_model=list[FreeSlotResponse]
)
def free_slots(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_free_slots(db, current_user.id)


@router.get(
    "/focus-window",
    response_model=FocusWindowResponse | None
)
def best_focus_window(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_best_focus_window(db, current_user.id)


@router.get(
    "/analytics",
    response_model=MeetingAnalyticsResponse
)
def meeting_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_meeting_analytics(db, current_user.id)


# ===========================
# Get By ID
# ===========================

@router.get(
    "/{meeting_id}",
    response_model=MeetingResponse
)
def fetch_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    meeting = get_meeting_by_id(
        db,
        current_user.id,
        meeting_id
    )

    if meeting is None:
        raise HTTPException(
            status_code=404,
            detail="Meeting not found"
        )

    return meeting