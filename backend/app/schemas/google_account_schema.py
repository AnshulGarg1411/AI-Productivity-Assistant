from datetime import datetime
from pydantic import BaseModel


class GoogleAccountCreate(BaseModel):

    user_id: int

    google_email: str

    access_token: str

    refresh_token: str | None = None

    expires_at: datetime | None = None

    scope: str | None = None


class GoogleAccountResponse(GoogleAccountCreate):

    id: int

    created_at: datetime

    class Config:

        from_attributes = True