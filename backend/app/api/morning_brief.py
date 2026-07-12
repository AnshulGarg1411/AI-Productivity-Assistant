from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.user import User

from app.core.dependencies import get_current_user

from app.schemas.morning_brief_schema import (
    MorningBriefResponse
)

from app.services.morning_brief_service import (
    get_morning_brief
)

router = APIRouter(

    prefix="/morning-brief",

    tags=["Morning Brief"]

)


@router.get(

    "/",

    response_model=MorningBriefResponse

)
def morning_brief(

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )

):

    return get_morning_brief(

        db,

        current_user

    )