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


class CommandResponse(BaseModel):
    """Combined AI + ticket result."""

    ai_result: dict[str, object] | str
    ticket_result: dict[str, object] | list[dict[str, object]] | None
