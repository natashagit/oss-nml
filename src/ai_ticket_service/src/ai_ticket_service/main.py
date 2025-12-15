"""FastAPI service that orchestrates AI intent extraction and ticket creation."""

import logging
import os
import uvicorn
from typing import Any
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from trello_client_impl.oauth import TrelloOAuthHandler  # type: ignore[import-untyped]
from trello_ticket_impl.trello_ticket_impl import TrelloTicketClientImpl  # type: ignore[import-untyped]

import openai_impl  # noqa: F401 - registers default AI implementation
from ai_api import AIInterface, get_client  # type: ignore[attr-defined]
from ai_ticket_service import tickets_api_compat  # noqa: F401 - Import compatibility layer early
from ai_ticket_service.models import CommandRequest, CommandResponse, HealthCheckResponse
from tickets_api import Ticket, TicketInterface, TicketStatus
from tickets_client_impl import TicketsClient  # Import at module level for integration tests

app = FastAPI(
    title="AI Ticket Orchestration Service",
    description="Natural language to ticket actions via AI + ticket client",
    version="0.1.0",
)

load_dotenv()
logger = logging.getLogger(__name__)


class TicketBackendFactory:
    """Factory for creating ticket backend clients."""

    @staticmethod
    def create_backend(backend_type: str) -> TicketInterface:
        """Create a ticket backend client.

        Args:
            backend_type: Type of backend ("google_tasks" or "trello")

        Returns:
            TicketInterface: Configured backend client

        Raises:
            ValueError: If backend type is not supported
            RuntimeError: If backend configuration is missing

        """
        if backend_type == "google_tasks":
            interactive = os.getenv("TASKS_INTERACTIVE", "false").lower() == "true"
            return TicketsClient(interactive=interactive)

        if backend_type == "trello":
            # Check required environment variables using their exact names
            token = os.getenv("TRELLO_TOKEN")
            board_id = os.getenv("TRELLO_BOARD_ID")

            if not token:
                msg = "TRELLO_TOKEN environment variable is required for Trello backend"
                raise RuntimeError(msg)
            if not board_id:
                msg = "TRELLO_BOARD_ID environment variable is required for Trello backend"
                raise RuntimeError(msg)

            # Set default REDIRECT_URI if not provided (following their pattern)
            if not os.getenv("REDIRECT_URI"):
                os.environ["REDIRECT_URI"] = "http://localhost:8000/callback"

            # Create OAuth handler using their from_env method (validates TRELLO_API_KEY, TRELLO_API_SECRET, REDIRECT_URI)
            oauth_handler = TrelloOAuthHandler.from_env()

            # Use their exact parameter names and approach
            return TrelloTicketClientImpl(  # type: ignore[no-any-return]
                token=token,
                oauth_handler=oauth_handler,
                board_id=board_id,
            )

        msg = f"Unsupported backend type: {backend_type}"
        raise ValueError(msg)


def _get_backend_status(backend_type: str) -> str:
    """Check if backend is properly configured."""
    try:
        TicketBackendFactory.create_backend(backend_type)
    except (ValueError, RuntimeError) as e:
        logger.warning("Backend %s not configured: %s", backend_type, e)
        return "not_configured"
    else:
        return "success"


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
    """Process natural language into ticket operations with backend selection."""
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
    backend_status = _get_backend_status(request.backend)

    if isinstance(ai_result, dict) and backend_status == "success":
        try:
            tickets_client = TicketBackendFactory.create_backend(request.backend)
            ticket_result = _handle_intent(ai_result, tickets_client)
        except (ValueError, RuntimeError):
            logger.exception("Failed to process ticket operation")
            backend_status = "error"

    return CommandResponse(
        ai_result=ai_result,
        ticket_result=ticket_result,
        backend_used=request.backend,
        backend_status=backend_status,
    )


def _parse_status(status_str: str | None) -> TicketStatus | None:
    if not status_str:
        return None
    try:
        # Map common status strings to TicketStatus enum values
        status_mapping = {
            "open": TicketStatus.OPEN,
            "in progress": TicketStatus.IN_PROGRESS,
            "in_progress": TicketStatus.IN_PROGRESS,
            "closed": TicketStatus.CLOSED,
            "done": TicketStatus.CLOSED,
        }
        normalized = status_str.lower().strip()
        return status_mapping.get(normalized)
    except ValueError:
        return None


def _handle_create_ticket(ai_result: dict[str, Any], tickets_client: TicketInterface) -> dict[str, Any]:
    """Handle create_ticket intent."""
    title = ai_result.get("title", f"AI Ticket {uuid4()}")
    description = ai_result.get("description", "")
    created = tickets_client.create_ticket(title=title, description=description)
    if not created:
        logger.error("Failed to create ticket with title: %s", title)
        return {}
    return _serialize_ticket(created)


def _handle_update_ticket(ai_result: dict[str, Any], tickets_client: TicketInterface) -> dict[str, Any]:
    """Handle update_ticket intent."""
    ticket_id = ai_result.get("ticket_id")
    if not ticket_id:
        return {}

    # Check if ticket exists before attempting update
    existing_ticket = tickets_client.get_ticket(ticket_id)
    if not existing_ticket:
        logger.warning("Ticket %s not found for update", ticket_id)
        return {}

    status = _parse_status(ai_result.get("status"))
    title = ai_result.get("title") if ai_result.get("title") else None
    # Only pass non-None values to update_ticket
    kwargs = {"ticket_id": ticket_id}
    if status is not None:
        kwargs["status"] = status
    if title:
        kwargs["title"] = title
    updated = tickets_client.update_ticket(**kwargs)
    if not updated:
        logger.error("Failed to update ticket %s", ticket_id)
        return {}
    return _serialize_ticket(updated)


def _handle_intent(
    ai_result: dict[str, Any],
    tickets_client: TicketInterface,
) -> dict[str, Any] | list[dict[str, Any]] | None:
    intent = ai_result.get("intent")

    if intent == "create_ticket":
        return _handle_create_ticket(ai_result, tickets_client)

    if intent == "get_ticket":
        ticket_id = ai_result.get("ticket_id")
        if ticket_id:
            found = tickets_client.get_ticket(ticket_id)
            return _serialize_ticket(found) if found else None

    if intent == "search_tickets":
        raw_query = ai_result.get("query")
        query = raw_query if isinstance(raw_query, str) and raw_query.strip() else None
        status = _parse_status(ai_result.get("status"))
        matches = tickets_client.search_tickets(query=query, status=status)
        return [_serialize_ticket(ticket) for ticket in matches]

    if intent == "update_ticket":
        return _handle_update_ticket(ai_result, tickets_client)

    if intent == "delete_ticket":
        ticket_id = ai_result.get("ticket_id")
        if ticket_id:
            # Check if ticket exists before attempting deletion
            existing_ticket = tickets_client.get_ticket(ticket_id)
            if not existing_ticket:
                logger.warning("Ticket %s not found for deletion", ticket_id)
                return {"deleted": False, "ticket_id": ticket_id, "error": "Ticket not found"}
            success = tickets_client.delete_ticket(ticket_id)
            return {"deleted": success, "ticket_id": ticket_id}

    return None


if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(
        "ai_ticket_service.main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8002")),
        reload=True,
    )
