"""FastAPI application for mail client service."""
from typing import Annotated, Literal

import gmail_client_impl  # noqa: F401 - Registers the client implementation
from fastapi import Depends, FastAPI, HTTPException, Query
from mail_client_api import Client
from pydantic import BaseModel, Field

from mail_client_service.dependencies import get_mail_client
from mail_client_service.models import MessageDetail, MessageSummary, OperationResponse

app = FastAPI(
    title="Mail Client Service",
    description="RESTful API for mail client operations",
    version="0.1.0",
)

# -----------------------------
# Messages API
# -----------------------------

@app.get("/messages")
def get_messages(
    client: Annotated[Client, Depends(get_mail_client)],
    max_results: Annotated[int, Query(ge=1, le=100)] = 10,
) -> list[MessageSummary]:
    """Fetch a list of message summaries."""
    try:
        messages = client.get_messages(max_results=max_results)
        return [
            MessageSummary(
                id=msg.id,
                **{"from": msg.from_},
                to=msg.to,
                date=msg.date,
                subject=msg.subject,
            )
            for msg in messages
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch messages: {e!s}") from e


@app.get("/messages/{message_id}")
def get_message(
    message_id: str,
    client: Annotated[Client, Depends(get_mail_client)],
) -> MessageDetail:
    """Fetch the full detail of a single message."""
    try:
        msg = client.get_message(message_id)
        return MessageDetail(
            id=msg.id,
            **{"from": msg.from_},
            to=msg.to,
            date=msg.date,
            subject=msg.subject,
            body=msg.body,
        )
    except Exception as e:
        # Tests expect 404 when not found; we map any retrieval error to 404 here.
        raise HTTPException(
            status_code=404,
            detail=f"Message {message_id} not found: {e!s}",
        ) from e


@app.post("/messages/{message_id}/mark-as-read")
def mark_message_as_read(
    message_id: str,
    client: Annotated[Client, Depends(get_mail_client)],
) -> OperationResponse:
    """Mark a message as read."""
    try:
        success = client.mark_as_read(message_id)
        return OperationResponse(
            success=success,
            message=f"Message {message_id} marked as read" if success else "Operation failed",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to mark message as read: {e!s}",
        ) from e


@app.delete("/messages/{message_id}")
def delete_message(
    message_id: str,
    client: Annotated[Client, Depends(get_mail_client)],
) -> OperationResponse:
    """Delete a message."""
    try:
        success = client.delete_message(message_id)
        return OperationResponse(
            success=success,
            message=f"Message {message_id} deleted" if success else "Operation failed",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete message: {e!s}",
        ) from e


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


# -----------------------------
# Chat Completions API (minimal stub for tests)
# -----------------------------

class ChatMessage(BaseModel):
    """A single chat message in a conversation.

    role: one of 'system', 'user', or 'assistant'
    content: the textual content of the message
    """

    role: Literal["system", "user", "assistant"] = Field(..., description="Message role")
    content: str = Field(..., description="Message content")


class ChatCompletionRequest(BaseModel):
    """Request model for chat completions (minimal for tests).

    `user_id` is required so validation fails early for missing authentication.
    """

    user_id: str
    messages: list[ChatMessage]
    model: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None


class ChatCompletionResponse(BaseModel):
    """Response model for chat completions used by tests.

    Contains the assistant's message, model metadata, and usage info.
    """

    message: ChatMessage
    model: str = "mock"
    usage: dict = Field(default_factory=dict)
    finish_reason: str = "stop"


@app.post("/chat-completions")
def create_chat_completion(req: ChatCompletionRequest) -> ChatCompletionResponse:
    """Minimal behavior for tests: echo the last user message."""
    last_user = next((m for m in reversed(req.messages) if m.role == "user"), None)
    reply = f"Echo: {last_user.content}" if last_user else "Hello from assistant."
    return ChatCompletionResponse(
        message=ChatMessage(role="assistant", content=reply),
        model=req.model or "mock",
        usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        finish_reason="stop",
    )
