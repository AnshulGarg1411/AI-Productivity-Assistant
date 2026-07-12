from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.user_schema import UserCreate
from app.services.user_service import (
    create_user,
    get_all_users
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/")
def users(db: Session = Depends(get_db)):
    return get_all_users(db)


@router.post("/")
def add_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    return create_user(
        db,
        user.name,
        user.email
    )