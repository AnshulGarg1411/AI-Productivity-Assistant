"""
The chat agent's core loop: bind tools to the Gemini chat model, let it
decide which to call, execute them against the real DB, feed results back,
repeat until it produces a final answer.

This is written by hand rather than using LangChain's create_agent (which
is built on LangGraph internally) or the older AgentExecutor -- full control
over the loop, and no LangGraph anywhere in the dependency tree.
"""
import logging

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.ai.chat.tools import build_tools

logger = logging.getLogger("app.ai")

MAX_TOOL_ITERATIONS = 5

SYSTEM_PROMPT = (
    "You are a productivity assistant with access to the user's tasks, "
    "meetings, and emails through tools. Use the tools to answer questions "
    "and take actions the user asks for. Always use a tool to look up "
    "real data rather than guessing -- never invent task/meeting/email "
    "details. Be concise in your final answers."
)


class ChatAgentUnavailable(Exception):
    """Raised when the chat agent can't run (e.g. no Gemini key configured)."""


def _get_model():
    if not settings.AI_FEATURES_ENABLED:
        return None

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.3,
        )
    except Exception:
        logger.exception("Failed to initialize chat model")
        return None


def run_chat_agent(
    db: Session,
    user: User,
    message: str,
    history: list[dict] | None = None,
) -> dict:
    """
    history is an optional list of {"role": "user"|"assistant", "content": str}
    from prior turns in this conversation.

    Returns {"reply": str, "tool_calls": list[str]}.
    Raises ChatAgentUnavailable if there's no Gemini key configured.
    """

    model = _get_model()

    if model is None:
        raise ChatAgentUnavailable(
            "The chat agent requires a GEMINI_API_KEY to be configured."
        )

    tools = build_tools(db, user)
    tools_by_name = {t.name: t for t in tools}
    model_with_tools = model.bind_tools(tools)

    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    for turn in history or []:
        if turn.get("role") == "assistant":
            messages.append(AIMessage(content=turn["content"]))
        else:
            messages.append(HumanMessage(content=turn["content"]))

    messages.append(HumanMessage(content=message))

    tool_calls_made = []

    for _ in range(MAX_TOOL_ITERATIONS):
        response = model_with_tools.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            return {
                "reply": response.content,
                "tool_calls": tool_calls_made,
            }

        for call in response.tool_calls:
            tool_fn = tools_by_name.get(call["name"])

            if tool_fn is None:
                result = f"Unknown tool: {call['name']}"
            else:
                try:
                    result = tool_fn.invoke(call["args"])
                except Exception as exc:
                    logger.exception(
                        "Tool %s failed during chat agent run", call["name"]
                    )
                    result = f"Tool {call['name']} failed: {exc}"

            tool_calls_made.append(call["name"])

            messages.append(
                ToolMessage(content=str(result), tool_call_id=call["id"])
            )

    # Hit the iteration cap without a final answer -- fail safe rather than
    # looping forever or returning nothing.
    return {
        "reply": (
            "I wasn't able to finish that request in a reasonable number "
            "of steps. Try rephrasing or breaking it into smaller asks."
        ),
        "tool_calls": tool_calls_made,
    }
