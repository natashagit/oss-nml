"""FastAPI application for mail client service."""

from typing import Annotated

import gmail_client_impl  # noqa: F401 - Registers the client implementation
from fastapi import Depends, FastAPI, HTTPException, Query
from mail_client_api import Client

from mail_client_service.dependencies import get_mail_client
from mail_client_service.models import MessageDetail, MessageSummary, OperationResponse

app = FastAPI(
    title="Mail Client Service",
    description="RESTful API for mail client operations",
    version="0.1.0",
)


@app.get("/messages")
def get_messages(
    max_results: Annotated[int, Query(ge=1, le=100)] = 10,
    client: Client = Depends(get_mail_client),
) -> list[MessageSummary]:
    """Fetch a list of message summaries.

    Args:
        max_results: Maximum number of messages to return (default: 10, max: 100)
        client: Injected mail client instance

    Returns:
        List of message summaries

    """
    try:
        messages = client.get_messages(max_results=max_results)
        return [
            MessageSummary(
                id=msg.id,
                from_=msg.from_,
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
    """Fetch the full detail of a single message.

    Args:
        message_id: The unique identifier of the message
        client: Injected mail client instance

    Returns:
        Full message details

    Raises:
        HTTPException: If message not found or retrieval fails

    """
    try:
        msg = client.get_message(message_id)
        return MessageDetail(
            id=msg.id,
            from_=msg.from_,
            to=msg.to,
            date=msg.date,
            subject=msg.subject,
            body=msg.body,
        )
    except Exception as e:
        raise HTTPException(
            status_code=404, detail=f"Message {message_id} not found: {e!s}",
        ) from e


@app.post("/messages/{message_id}/mark-as-read")
def mark_message_as_read(
    message_id: str,
    client: Annotated[Client, Depends(get_mail_client)],
) -> OperationResponse:
    """Mark a message as read.

    Args:
        message_id: The unique identifier of the message
        client: Injected mail client instance

    Returns:
        Operation response with success status

    """
    try:
        success = client.mark_as_read(message_id)
        return OperationResponse(
            success=success,
            message=f"Message {message_id} marked as read" if success else "Operation failed",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to mark message as read: {e!s}",
        ) from e


@app.delete("/messages/{message_id}")
def delete_message(
    message_id: str,
    client: Annotated[Client, Depends(get_mail_client)],
) -> OperationResponse:
    """Delete a message.

    Args:
        message_id: The unique identifier of the message
        client: Injected mail client instance

    Returns:
        Operation response with success status

    """
    try:
        success = client.delete_message(message_id)
        return OperationResponse(
            success=success,
            message=f"Message {message_id} deleted" if success else "Operation failed",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete message: {e!s}",
        ) from e


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Dictionary with status

    """
    return {"status": "healthy"}
