from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

from app.ai.chat.agent import run_chat_agent, ChatAgentUnavailable

router = APIRouter(
    prefix="/chat",
    tags=["Chat Agent"]
)


class ChatTurn(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatTurn] = []


class ChatResponse(BaseModel):
    reply: str
    tool_calls: list[str]


@router.post("/", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        result = run_chat_agent(
            db,
            current_user,
            request.message,
            [turn.model_dump() for turn in request.history],
        )
    except ChatAgentUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    return result
