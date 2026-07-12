from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

from starlette.middleware.sessions import SessionMiddleware
# Import all models
from app.models.user import User
from app.models.email import Email
from app.models.meeting import Meeting
from app.models.google_account import GoogleAccount
# Import routers
from app.api.users import router as user_router
from app.api.emails import router as email_router
from app.api.meetings import router as meeting_router
from app.api.tasks import router as task_router
from app.api.dashboard import (
    router as dashboard_router
)
from app.api.auth import (
    router as auth_router
)
from app.api.gmail import router as gmail_router
from app.api.calendar import (
    router as calendar_router
)
from app.api import morning_brief
from app.api.chat import router as chat_router
# Schema is now managed by Alembic migrations (see backend/alembic/), not
# create_all. Run `alembic upgrade head` before starting the server.

app = FastAPI(
    title="AI Productivity Assistant API"
)
from app.core.config import settings

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET,
    https_only=False,
    same_site="lax"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger("app")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    # Pydantic's default 422 body is verbose and inconsistent with the rest
    # of the API's error shape. Normalize it to {detail, errors}.
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Invalid request data.",
            "errors": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Never leak stack traces / internal details to the client. Log the
    # real exception server-side, return a generic message to the caller.
    logger.exception("Unhandled exception on %s %s", request.method, request.url)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again."},
    )

app.include_router(user_router)
app.include_router(email_router)
app.include_router(meeting_router)
app.include_router(task_router)
app.include_router(
    dashboard_router
)
app.include_router(auth_router)
app.include_router(gmail_router)
app.include_router(
    calendar_router
)
app.include_router(
    morning_brief.router
)
app.include_router(chat_router)
@app.get("/")
def home():
    return {
        "message": "AI Productivity Assistant API"
    }