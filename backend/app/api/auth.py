from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.config import settings
from app.services.auth_service import login_google_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

oauth = OAuth()

oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": (
            "openid "
            "email "
            "profile "
            "https://www.googleapis.com/auth/gmail.readonly "
            "https://www.googleapis.com/auth/calendar.readonly"
        )
    }
)


@router.get("/login")
async def login(request: Request):

    redirect_uri = request.url_for("callback")

    return await oauth.google.authorize_redirect(
        request,
        redirect_uri
    )


@router.get(
    "/callback",
    name="callback"
)
async def callback(
    request: Request,
    db: Session = Depends(get_db)
):

    token = await oauth.google.authorize_access_token(
        request
    )

    result = login_google_user(
        db,
        token
    )

    # The browser lands here directly after Google redirects back (this is a
    # full-page navigation, not an SPA fetch call), so we can't just return
    # JSON -- the React app would never see it. Instead we hand the JWT to
    # the frontend via a redirect, and a dedicated frontend route picks it
    # up from the URL and stores it.
    frontend_redirect = (
        f"{settings.FRONTEND_URL}/oauth/callback"
        f"?token={result['access_token']}"
    )

    return RedirectResponse(url=frontend_redirect)

from app.core.dependencies import (
    get_current_user
)

from app.models.user import User


@router.get("/me")
def me(

    current_user: User = Depends(
        get_current_user
    )

):

    return current_user