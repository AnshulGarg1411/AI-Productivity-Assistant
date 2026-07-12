import logging

from fastapi import HTTPException

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from sqlalchemy.orm import Session

from app.models.google_account import GoogleAccount
from app.core.config import settings

logger = logging.getLogger(__name__)


def build_google_service(
    db: Session,
    user_id: int,
    api_name: str,
    version: str,
    scopes: list[str]
):

    account = (
        db.query(GoogleAccount)
        .filter(GoogleAccount.user_id == user_id)
        .first()
    )

    if account is None:

        logger.error(
            "Google account not found for user %s",
            user_id
        )

        raise HTTPException(
            status_code=404,
            detail="Google account not connected."
        )

    credentials = Credentials(
        token=account.access_token,
        refresh_token=account.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=scopes
    )

    try:

        if credentials.expired and credentials.refresh_token:

            logger.info(
                "Refreshing Google token for user %s",
                user_id
            )

            credentials.refresh(Request())

            account.access_token = credentials.token

            if credentials.expiry:

                account.expires_at = credentials.expiry

            db.commit()

    except Exception as e:

        logger.exception(e)

        raise HTTPException(
            status_code=401,
            detail="Unable to refresh Google credentials."
        )

    return build(
        api_name,
        version,
        credentials=credentials
    )