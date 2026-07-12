from datetime import datetime, timedelta

from jose import jwt, JWTError

from app.core.config import settings

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_DAYS = 7


def create_access_token(
    user_id: int
):

    expire = datetime.utcnow() + timedelta(
        days=ACCESS_TOKEN_EXPIRE_DAYS
    )

    payload = {

        "sub": str(user_id),

        "exp": expire

    }

    return jwt.encode(

        payload,

        settings.JWT_SECRET,

        algorithm=ALGORITHM

    )


def verify_access_token(token: str):

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:
        return None