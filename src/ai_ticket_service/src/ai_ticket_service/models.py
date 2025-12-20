"""Pydantic models for AI + Ticket service."""

from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    """Health payload."""

    status: str
    version: str


class CommandRequest(BaseModel):
    """Incoming natural language command for ticket creation."""

    user_input: str
    system_prompt: str = "You are a strict router that extracts intent, title, description."
    backend: str = "google_tasks"  # Options: "google_tasks" or "trello"


class CommandResponse(BaseModel):
    """Combined AI + ticket result."""

    ai_result: dict[str, object] | str
    ticket_result: dict[str, object] | list[dict[str, object]] | None
    backend_used: str
    backend_status: str
    formatted_response: str | None = None


class ChatCommandRequest(BaseModel):
    """Chat relay payload."""

    user_input: str
