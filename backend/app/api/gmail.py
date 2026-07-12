from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

from app.services.gmail_service import (
    sync_gmail
)

router = APIRouter(
    prefix="/gmail",
    tags=["Gmail"]
)


@router.post("/sync")
def gmail_sync(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return sync_gmail(
        db,
        current_user.id
    )