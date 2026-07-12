from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.email_schema import (
    EmailCreate,
    EmailResponse,
    EmailSummaryResponse,
    EmailReplyResponse
)

from app.services.email_service import (
    create_email,
    get_all_emails,
    get_email_by_id,
    get_unread_emails,
    get_important_emails,
    get_starred_emails,
    get_archived_emails,
    get_urgent_emails,
    search_emails,
    mark_as_read,
    archive_email,
    unarchive_email,
    star_email,
    unstar_email,
    delete_email
)

from app.core.dependencies import (
    get_current_user
)

from app.models.user import User

from app.ai.email_intelligence_agent import analyze_email
from app.ai.email_reply_agent import generate_reply, SmartReplyUnavailable
from pydantic import BaseModel

router = APIRouter(

    prefix="/emails",

    tags=["Emails"]

)


# =====================================================
# GET ALL EMAILS
# =====================================================

@router.get(
    "/",
    response_model=list[EmailResponse]
)
def fetch_all_emails(

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )

):

    return get_all_emails(

        db,

        current_user.id

    )


# =====================================================
# GET UNREAD EMAILS
# =====================================================

@router.get(
    "/unread",
    response_model=list[EmailResponse]
)
def fetch_unread_emails(

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )

):

    return get_unread_emails(

        db,

        current_user.id

    )


# =====================================================
# IMPORTANT EMAILS
# =====================================================

@router.get(
    "/important",
    response_model=list[EmailResponse]
)
def fetch_important_emails(

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )

):

    return get_important_emails(

        db,

        current_user.id

    )


# =====================================================
# STARRED EMAILS
# =====================================================

@router.get(
    "/starred",
    response_model=list[EmailResponse]
)
def fetch_starred_emails(

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )

):

    return get_starred_emails(

        db,

        current_user.id

    )


# =====================================================
# ARCHIVED EMAILS
# =====================================================

@router.get(
    "/archived",
    response_model=list[EmailResponse]
)
def fetch_archived_emails(

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )

):

    return get_archived_emails(

        db,

        current_user.id

    )


# =====================================================
# URGENT EMAILS
# =====================================================

@router.get(
    "/urgent"
)
def fetch_urgent_emails(

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )

):

    return get_urgent_emails(

        db,

        current_user.id

    )


# =====================================================
# SEARCH EMAILS
# =====================================================

@router.get("/search")
def search(

    q: str,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )

):

    return search_emails(

        db,

        current_user.id,

        q

    )


# =====================================================
# GET EMAIL BY ID
# =====================================================

@router.get(
    "/{email_id}",
    response_model=EmailResponse
)
def fetch_email(

    email_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )

):

    email = get_email_by_id(

        db,

        current_user.id,

        email_id

    )

    if email is None:

        raise HTTPException(

            status_code=404,

            detail="Email not found"

        )

    return email


# =====================================================
# AI: SUMMARIZE + CATEGORIZE + PRIORITIZE (on demand)
# =====================================================

@router.post(
    "/{email_id}/summarize",
    response_model=EmailSummaryResponse
)
def summarize_email(

    email_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )

):

    email = get_email_by_id(
        db,
        current_user.id,
        email_id
    )

    if email is None:
        raise HTTPException(
            status_code=404,
            detail="Email not found"
        )

    analyze_email(db, email)

    if not email.ai_summary:
        raise HTTPException(
            status_code=503,
            detail=(
                "Email summary is unavailable -- check that GEMINI_API_KEY "
                "is configured, and that this email wasn't already "
                "analyzed with a different (empty) result."
            ),
        )

    return EmailSummaryResponse(summary=email.ai_summary)


# =====================================================
# AI: SMART REPLY (on demand)
# =====================================================

class SmartReplyRequest(BaseModel):
    tone: str = "friendly"


@router.post(
    "/{email_id}/reply",
    response_model=EmailReplyResponse
)
def smart_reply(

    email_id: int,

    request: SmartReplyRequest,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )

):

    email = get_email_by_id(
        db,
        current_user.id,
        email_id
    )

    if email is None:
        raise HTTPException(
            status_code=404,
            detail="Email not found"
        )

    try:
        reply = generate_reply(email, request.tone)
    except SmartReplyUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    return EmailReplyResponse(reply=reply)

@router.post(
    "/",
    response_model=EmailResponse,
    status_code=201
)
def add_email(

    email: EmailCreate,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )

):

    email_data = email.model_dump()

    email_data["user_id"] = current_user.id

    return create_email(

        db,

        email_data

    )


# =====================================================
# MARK EMAIL AS READ
# =====================================================

@router.patch(
    "/{email_id}/read",
    response_model=EmailResponse
)
def read_email(

    email_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )

):

    email = mark_as_read(

        db,

        current_user.id,

        email_id

    )

    if email is None:

        raise HTTPException(

            status_code=404,

            detail="Email not found"

        )

    return email


# =====================================================
# STAR EMAIL
# =====================================================

@router.patch(
    "/{email_id}/star",
    response_model=EmailResponse
)
def star(

    email_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )

):

    email = star_email(

        db,

        current_user.id,

        email_id

    )

    if email is None:

        raise HTTPException(

            status_code=404,

            detail="Email not found"

        )

    return email


# =====================================================
# UNSTAR EMAIL
# =====================================================

@router.patch(
    "/{email_id}/unstar",
    response_model=EmailResponse
)
def unstar(

    email_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )

):

    email = unstar_email(

        db,

        current_user.id,

        email_id

    )

    if email is None:

        raise HTTPException(

            status_code=404,

            detail="Email not found"

        )

    return email


# =====================================================
# ARCHIVE EMAIL
# =====================================================

@router.patch(
    "/{email_id}/archive",
    response_model=EmailResponse
)
def archive(

    email_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )

):

    email = archive_email(

        db,

        current_user.id,

        email_id

    )

    if email is None:

        raise HTTPException(

            status_code=404,

            detail="Email not found"

        )

    return email


# =====================================================
# UNARCHIVE EMAIL
# =====================================================

@router.patch(
    "/{email_id}/unarchive",
    response_model=EmailResponse
)
def unarchive(

    email_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )

):

    email = unarchive_email(

        db,

        current_user.id,

        email_id

    )

    if email is None:

        raise HTTPException(

            status_code=404,

            detail="Email not found"

        )

    return email


# =====================================================
# DELETE EMAIL
# =====================================================

@router.delete(
    "/{email_id}"
)
def remove_email(

    email_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )

):

    deleted = delete_email(

        db,

        current_user.id,

        email_id

    )

    if not deleted:

        raise HTTPException(

            status_code=404,

            detail="Email not found"

        )

    return {

        "message": "Email deleted successfully"

    }