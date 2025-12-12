"""Entry point for demonstrating AI + Ticket orchestration via the adapter."""

import logging
import os
from typing import Any

from dotenv import load_dotenv

from ai_ticket_adapter import TicketOrchestrationAdapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

SYSTEM_PROMPT = "You route user requests into structured ticket commands."


def _call(adapter: TicketOrchestrationAdapter, user_input: str) -> dict[str, Any]:
    resp = adapter.raw_response(user_input=user_input, system_prompt=SYSTEM_PROMPT)
    print("AI result:", resp.ai_result)  # noqa: T201
    print("Ticket result:", resp.ticket_result)  # noqa: T201
    return {
        "ai_result": resp.ai_result,
        "ticket_result": resp.ticket_result,
    }


def main() -> None:
    """Exercise create/get/search/update/delete via the orchestration service."""
    base_url = os.getenv("AI_TICKET_SERVICE_URL", "http://127.0.0.1:8000")
    adapter = TicketOrchestrationAdapter(base_url=base_url)
    logger.info("Calling AI Ticket service at %s", base_url)

    # 1) Create
    print("\n=== CREATE ===")  # noqa: T201
    create_data = _call(
        adapter,
        "Create a ticket to add rate limiting to the public API and monitor 429s.",
    )
    ticket_id = None
    if isinstance(create_data["ticket_result"], dict):
        ticket_id = create_data["ticket_result"].get("id")

    if not ticket_id:
        print("No ticket id produced; cannot continue further ops.")  # noqa: T201
        return

    # 2) Get
    print("\n=== GET ===")  # noqa: T201
    _call(adapter, f"Fetch the ticket with ID {ticket_id}.")

    # 3) Search
    print("\n=== SEARCH ===")  # noqa: T201
    _call(adapter, "List open tickets mentioning API.")

    # 4) Update
    print("\n=== UPDATE ===")  # noqa: T201
    _call(
        adapter,
        f"Mark ticket {ticket_id} as completed and title it 'API rate limit deployed'.",
    )

    # 5) Delete
    print("\n=== DELETE ===")  # noqa: T201
    _call(adapter, f"Delete ticket {ticket_id}.")

    print("\nDemo complete.")  # noqa: T201


if __name__ == "__main__":
    main()
