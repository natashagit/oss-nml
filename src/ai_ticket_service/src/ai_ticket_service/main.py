"""FastAPI service that orchestrates AI intent extraction and ticket creation."""

import logging
import os
from typing import Any
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

import openai_impl  # noqa: F401 - registers default AI implementation
from ai_api import AIInterface, get_client  # type: ignore[attr-defined]
from ai_ticket_service.models import CommandRequest, CommandResponse, HealthCheckResponse
from tickets_api import Ticket, TicketStatus
from tickets_client_impl import TicketsClient

app = FastAPI(
    title="AI Ticket Orchestration Service",
    description="Natural language to ticket actions via AI + ticket client",
    version="0.1.0",
)

load_dotenv()
logger = logging.getLogger(__name__)


def _serialize_ticket(ticket: Ticket) -> dict[str, Any]:
    """Convert Ticket to JSON-serializable dict."""
    return {
        "id": ticket.id,
        "title": ticket.title,
        "description": ticket.description,
        "status": ticket.status.value if isinstance(ticket.status, TicketStatus) else str(ticket.status),
        "assignee": ticket.assignee,
    }


def _ai_generate(request: CommandRequest, schema_override: dict[str, Any]) -> str | dict[str, Any]:
    """Call AI with enforced schema to extract ticket command."""
    try:
        client: AIInterface = get_client()  # type: ignore[assignment]
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Failed to load AI client: {exc!s}") from exc

    try:
        return client.generate_response(
            user_input=request.user_input,
            system_prompt=request.system_prompt,
            response_schema=schema_override,
        )
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Generation failed: {exc!s}") from exc


@app.get("/health")
def health() -> HealthCheckResponse:
    """Health check."""
    return HealthCheckResponse(status="healthy", version=app.version or "0.0.0")


@app.post("/command")
def command(request: CommandRequest) -> CommandResponse:
    """Process natural language into ticket operations."""
    schema = {
        "name": "ticket_command",
        "description": "Extract ticketing intent and relevant fields",
        "schema": {
            "type": "object",
            "properties": {
                "intent": {
                    "type": "string",
                    "enum": [
                        "create_ticket",
                        "get_ticket",
                        "search_tickets",
                        "update_ticket",
                        "delete_ticket",
                    ],
                },
                "title": {"type": "string"},
                "description": {"type": "string"},
                "ticket_id": {"type": "string"},
                "query": {"type": "string"},
                "status": {"type": "string"},
            },
            "required": ["intent", "title", "description", "ticket_id", "query", "status"],
            "additionalProperties": False,
        },
    }

    ai_result = _ai_generate(request, schema_override=schema)

    ticket_result: dict[str, Any] | list[dict[str, Any]] | None = None
    if isinstance(ai_result, dict):
        interactive = os.getenv("TASKS_INTERACTIVE", "false").lower() == "true"
        tickets_client = TicketsClient(interactive=interactive)
        ticket_result = _handle_intent(ai_result, tickets_client)

    return CommandResponse(ai_result=ai_result, ticket_result=ticket_result)


def _parse_status(status_str: str | None) -> TicketStatus | None:
    if not status_str:
        return None
    try:
        return TicketStatus(status_str.lower())
    except ValueError:
        return None


def _handle_intent(
    ai_result: dict[str, Any],
    tickets_client: TicketsClient,
) -> dict[str, Any] | list[dict[str, Any]] | None:
    intent = ai_result.get("intent")
    result: dict[str, Any] | list[dict[str, Any]] | None = None

    if intent == "create_ticket":
        title = ai_result.get("title", f"AI Ticket {uuid4()}")
        description = ai_result.get("description", "")
        created = tickets_client.create_ticket(title=title, description=description)
        result = _serialize_ticket(created)

    if intent == "get_ticket":
        ticket_id = ai_result.get("ticket_id")
        if ticket_id:
            found = tickets_client.get_ticket(ticket_id)
            result = _serialize_ticket(found) if found else None

    if intent == "search_tickets":
        raw_query = ai_result.get("query")
        query = raw_query if isinstance(raw_query, str) and raw_query.strip() else None
        status = _parse_status(ai_result.get("status"))
        matches = tickets_client.search_tickets(query=query, status=status)
        result = [_serialize_ticket(ticket) for ticket in matches]

    if intent == "update_ticket":
        ticket_id = ai_result.get("ticket_id")
        if ticket_id:
            status = _parse_status(ai_result.get("status"))
            title = ai_result.get("title")
            updated = tickets_client.update_ticket(ticket_id=ticket_id, status=status, title=title)
            result = _serialize_ticket(updated)

    if intent == "delete_ticket":
        ticket_id = ai_result.get("ticket_id")
        if ticket_id:
            success = tickets_client.delete_ticket(ticket_id)
            result = {"deleted": success, "ticket_id": ticket_id}

    return result


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(
        "ai_ticket_service.main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8002")),
        reload=True,
    )
