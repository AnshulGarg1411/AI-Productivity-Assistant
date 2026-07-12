from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.core.dependencies import (
    get_current_user
)

from app.models.user import User

from app.services.calendar_service import (
    sync_calendar
)

router = APIRouter(

    prefix="/calendar",

    tags=["Google Calendar"]

)


@router.get("/sync")
def calendar_sync(

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )

):

    return sync_calendar(

        db=db,

        user_id=current_user.id

    )