from datetime import datetime

from sqlalchemy.orm import Session

from app.models.google_account import GoogleAccount


def get_google_account_by_user_id(
    db: Session,
    user_id: int
):

    return (

        db.query(GoogleAccount)

        .filter(
            GoogleAccount.user_id == user_id
        )

        .first()

    )


def save_google_account(
    db: Session,
    user_id: int,
    google_email: str,
    token: dict
):

    expires = token.get("expires_at")

    if expires:

        expires = datetime.fromtimestamp(
            expires
        )

    account = get_google_account_by_user_id(
        db,
        user_id
    )

    if account:

        account.access_token = token["access_token"]

        account.refresh_token = token.get(
            "refresh_token"
        )

        account.scope = token.get(
            "scope"
        )

        account.expires_at = expires

    else:

        account = GoogleAccount(

            user_id=user_id,

            google_email=google_email,

            access_token=token["access_token"],

            refresh_token=token.get(
                "refresh_token"
            ),

            scope=token.get(
                "scope"
            ),

            expires_at=expires

        )

        db.add(account)

    db.commit()

    db.refresh(account)

    return account