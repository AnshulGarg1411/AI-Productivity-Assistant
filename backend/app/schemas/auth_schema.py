from pydantic import BaseModel


class UserInfo(BaseModel):

    id: int

    name: str

    email: str


class LoginResponse(BaseModel):

    access_token: str

    token_type: str

    user: UserInfo