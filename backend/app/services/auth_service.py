from sqlalchemy.orm import Session

from app.services.user_service import (
    get_user_by_email,
    create_user
)

from app.services.google_account_service import (
    save_google_account
)

from app.core.security import (
    create_access_token
)


def login_google_user(
    db: Session,
    token: dict
):

    user_info = token["userinfo"]

    email = user_info["email"]

    name = user_info["name"]

    user = get_user_by_email(
        db,
        email
    )

    if user is None:

        user = create_user(
            db,
            name,
            email
        )

    save_google_account(
        db,
        user.id,
        email,
        token
    )

    jwt_token = create_access_token(
        user.id
    )

    return {

        "access_token": jwt_token,

        "token_type": "Bearer",

        "user": {

            "id": user.id,

            "name": user.name,

            "email": user.email

        }

    }