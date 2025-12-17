"""FastAPI service that orchestrates AI intent extraction and ticket creation."""

import logging
import os
from typing import Any
from uuid import uuid4

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from slack_impl.slack_client import SlackClient  # type: ignore[import-untyped]
from trello_client_impl.oauth import TrelloOAuthHandler  # type: ignore[import-untyped]
from trello_ticket_impl.trello_ticket_impl import TrelloTicketClientImpl  # type: ignore[import-untyped]

import openai_impl  # noqa: F401 - registers default AI implementation
from ai_api import AIInterface, get_client  # type: ignore[attr-defined]
from ai_ticket_service import tickets_api_compat  # noqa: F401 - Import compatibility layer early
from ai_ticket_service.models import CommandRequest, CommandResponse, HealthCheckResponse, SlackCommandRequest
from tickets_api import Ticket, TicketInterface, TicketStatus
from tickets_client_impl import TicketsClient  # Import at module level for integration tests

app = FastAPI(
    title="AI Ticket Orchestration Service",
    description="Natural language to ticket actions via AI + ticket client",
    version="0.1.0",
)

load_dotenv()
logger = logging.getLogger(__name__)
DEFAULT_SYSTEM_PROMPT = "You are a strict router that extracts intent, title, description."


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


def _normalize_ticket_data(
    ticket_result: dict[str, Any] | list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    """Normalize ticket result into a list of dicts for formatting."""
    if ticket_result is None:
        return []
    if isinstance(ticket_result, list):
        return ticket_result
    return [ticket_result]


def _format_ticket_markdown(ticket_result: dict[str, Any] | list[dict[str, Any]] | None) -> str:
    """Render ticket results as Markdown suitable for Slack."""
    tickets = _normalize_ticket_data(ticket_result)
    if not tickets:
        return "No tickets were returned."

    sections: list[str] = []
    for idx, ticket in enumerate(tickets, start=1):
        sections.append(
            "\n".join(
                [
                    f"*Ticket {idx}*",
                    f"• *Title:* {ticket.get('title','(untitled)')}",
                    f"• *ID:* `{ticket.get('id','?')}`",
                    f"• *Status:* {ticket.get('status','unknown')}",
                    f"• *Description:* {ticket.get('description','')}",
                ],
            ),
        )
        if idx >= 5:
            break

    formatted = "\n\n".join(sections)
    if len(tickets) > 5:
        formatted += f"\n\n… and {len(tickets) - 5} more."
    return formatted


def _get_ai_client() -> AIInterface:
    """Return configured AI client or raise HTTPException."""
    try:
        client: AIInterface = get_client()  # type: ignore[assignment]
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Failed to load AI client: {exc!s}") from exc
    return client


def _ai_generate(
    client: AIInterface,
    request: CommandRequest,
    schema_override: dict[str, Any],
) -> str | dict[str, Any]:
    """Call AI with enforced schema to extract ticket command."""
    try:
        return client.generate_response(
            user_input=request.user_input,
            system_prompt=request.system_prompt,
            response_schema=schema_override,
        )
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Generation failed: {exc!s}") from exc


def _build_slack_client() -> SlackClient:
    """Configure Slack client based on environment."""
    offline = os.getenv("SLACK_OFFLINE", "false").lower() == "true"
    base_url = os.getenv("SLACK_BASE_URL")
    token = os.getenv("SLACK_BOT_TOKEN")

    if offline or not base_url or not token:
        logger.info("Slack client running in offline mode.")
        return SlackClient()

    logger.info("Slack client running in ONLINE mode (base_url=%s).", base_url)
    return SlackClient(base_url=base_url, token=token)


def _command_schema() -> dict[str, Any]:
    return {
        "name": "ticket_command",
        "description": (
            "Extract ticketing intent and relevant fields. Use 'chat' for conversational queries "
            "or 'unknown' when intent is unclear. When the user asks to list or show tickets "
            "(for example 'list all tickets', 'show my tickets'), set intent to 'search_tickets' "
            "with query set to null. Only use 'get_ticket' when a specific ticket ID is present."
        ),
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
                        "chat",
                        "unknown",
                    ],
                },
                "title": {"type": "string"},
                "description": {"type": "string"},
                "ticket_id": {"type": "string"},
                "query": {"type": "string"},
                "status": {"type": "string"},
                "message": {"type": "string", "description": "Response message for chat or unknown intents"},
            },
            "required": ["intent", "title", "description", "ticket_id", "query", "status", "message"],
            "additionalProperties": False,
        },
    }


def _execute_command(request: CommandRequest) -> CommandResponse:
    client = _get_ai_client()
    schema = _command_schema()

    ai_result = _ai_generate(client, request, schema_override=schema)
    ticket_result: dict[str, Any] | list[dict[str, Any]] | None = None
    backend_status = _get_backend_status(request.backend)

    if isinstance(ai_result, dict):
        intent = ai_result.get("intent")

        if intent in ("chat", "unknown"):
            if intent == "chat":
                message = ai_result.get("message", "I'm here to help with ticket operations.")
                ticket_result = {"type": "chat", "message": message}
            else:
                message = ai_result.get("message", "I'm not sure what you'd like me to do. Please specify a ticket operation.")
                ticket_result = {"type": "unknown", "message": message}
        elif backend_status == "success":
            try:
                tickets_client = TicketBackendFactory.create_backend(request.backend)
                ticket_result = _handle_intent(ai_result, tickets_client)
            except (ValueError, RuntimeError):
                logger.exception("Failed to process ticket operation")
                backend_status = "error"

    formatted_response = _format_ticket_markdown(ticket_result)

    return CommandResponse(
        ai_result=ai_result,
        ticket_result=ticket_result,
        backend_used=request.backend,
        backend_status=backend_status,
        formatted_response=formatted_response,
    )


@app.get("/health")
def health() -> HealthCheckResponse:
    """Health check."""
    return HealthCheckResponse(status="healthy", version=app.version or "0.0.0")


@app.post("/command")
def command(request: CommandRequest) -> CommandResponse:
    """Process natural language into ticket operations with backend selection."""
    return _execute_command(request)


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


def _handle_get_ticket(ai_result: dict[str, Any], tickets_client: TicketInterface) -> dict[str, Any] | None:
    """Handle get_ticket intent."""
    ticket_id = ai_result.get("ticket_id")
    if ticket_id:
        found = tickets_client.get_ticket(ticket_id)
        return _serialize_ticket(found) if found else None
    return None


def _handle_search_tickets(ai_result: dict[str, Any], tickets_client: TicketInterface) -> list[dict[str, Any]]:
    """Handle search_tickets intent."""
    raw_query = ai_result.get("query")
    query = raw_query if isinstance(raw_query, str) and raw_query.strip() else None
    status = _parse_status(ai_result.get("status"))
    matches = tickets_client.search_tickets(query=query, status=status)
    return [_serialize_ticket(ticket) for ticket in matches]


def _handle_delete_ticket(ai_result: dict[str, Any], tickets_client: TicketInterface) -> dict[str, Any] | None:
    """Handle delete_ticket intent."""
    ticket_id = ai_result.get("ticket_id")
    if not ticket_id:
        return None
    # Check if ticket exists before attempting deletion
    existing_ticket = tickets_client.get_ticket(ticket_id)
    if not existing_ticket:
        logger.warning("Ticket %s not found for deletion", ticket_id)
        return {"deleted": False, "ticket_id": ticket_id, "error": "Ticket not found"}
    success = tickets_client.delete_ticket(ticket_id)
    return {"deleted": success, "ticket_id": ticket_id}


def _handle_chat(ai_result: dict[str, Any], tickets_client: TicketInterface) -> dict[str, str]:  # noqa: ARG001
    """Handle chat intent."""
    message = ai_result.get("message", "I'm here to help with ticket operations.")
    return {"type": "chat", "message": message}


def _handle_unknown(ai_result: dict[str, Any], tickets_client: TicketInterface) -> dict[str, str]:  # noqa: ARG001
    """Handle unknown intent."""
    message = ai_result.get(
        "message",
        "I'm not sure what you'd like me to do. Please specify a ticket operation.",
    )
    return {"type": "unknown", "message": message}


def _handle_intent(
    ai_result: dict[str, Any],
    tickets_client: TicketInterface,
) -> dict[str, Any] | list[dict[str, Any]] | None:
    intent = ai_result.get("intent")

    # Dispatch table for intent handlers
    handlers = {
        "create_ticket": _handle_create_ticket,
        "get_ticket": _handle_get_ticket,
        "search_tickets": _handle_search_tickets,
        "update_ticket": _handle_update_ticket,
        "delete_ticket": _handle_delete_ticket,
        "chat": _handle_chat,
        "unknown": _handle_unknown,
    }

    if not isinstance(intent, str):
        return None

    handler = handlers.get(intent)
    return handler(ai_result, tickets_client) if handler else None


@app.post("/slack/command")
def slack_command(request: SlackCommandRequest) -> dict[str, str]:
    """Process a Slack message and post formatted results back to Slack."""
    backend = os.getenv("TICKET_BACKEND", "google_tasks")
    system_prompt = os.getenv("SLACK_SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT)
    channel_id = os.getenv("SLACK_CHANNEL_ID")

    if not channel_id:
        raise HTTPException(status_code=500, detail="SLACK_CHANNEL_ID not configured.")

    command_request = CommandRequest(
        user_input=request.user_input,
        system_prompt=system_prompt,
        backend=backend,
    )
    result = _execute_command(command_request)

    formatted = result.formatted_response or _format_ticket_markdown(result.ticket_result)
    slack_client = _build_slack_client()
    slack_client.post_message(channel_id, f"User: {request.user_input}")
    slack_client.post_message(channel_id, formatted)

    return {
        "status": "posted",
        "channel_id": channel_id,
        "backend_used": result.backend_used,
        "message": formatted,
    }


if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(
        "ai_ticket_service.main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8002")),
        reload=True,
    )
