"""Entry point for demonstrating the AI Ticket orchestration via the adapter."""

from __future__ import annotations

import logging
import os
from typing import Any

from dotenv import load_dotenv

from ai_ticket_adapter import TicketOrchestrationAdapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

SYSTEM_PROMPT = "You route user requests into structured ticket commands."


def _extract_id_from_item(item: object) -> str | None:
    if isinstance(item, dict):
        tid = item.get("id")
        if tid:
            return str(tid)
    if hasattr(item, "to_dict"):
        data = item.to_dict()  # type: ignore[no-untyped-call]
        tid = data.get("id")
        if tid:
            return str(tid)
    if hasattr(item, "additional_properties"):
        tid = getattr(item, "additional_properties", {}).get("id")
        if tid:
            return str(tid)
    return None


def _first_ticket_id(ticket_result: object) -> str | None:
    if isinstance(ticket_result, dict):
        return _extract_id_from_item(ticket_result)
    if hasattr(ticket_result, "to_dict") or hasattr(ticket_result, "additional_properties"):
        return _extract_id_from_item(ticket_result)
    if isinstance(ticket_result, list):
        for item in ticket_result:
            tid = _extract_id_from_item(item)
            if tid:
                return tid
    return None


def _call(adapter: TicketOrchestrationAdapter, user_input: str) -> dict[str, Any]:
    backend = os.getenv("TICKET_BACKEND", "google_tasks")
    resp = adapter.raw_response(
        user_input=user_input,
        system_prompt=SYSTEM_PROMPT,
        backend=backend,
    )
    print("AI result:", resp.ai_result)  # noqa: T201
    print("Ticket result:", resp.ticket_result)  # noqa: T201
    return {"ai_result": resp.ai_result, "ticket_result": resp.ticket_result}


def main() -> None:
    """Exercise create/search/get/update/delete via the AI Ticket service."""
    base_url = os.getenv("AI_TICKET_SERVICE_URL", "http://127.0.0.1:8000")
    adapter = TicketOrchestrationAdapter(base_url=base_url)
    logger.info("Calling AI Ticket service at %s", base_url)

    # 1) Create
    print("\n=== CREATE ===")  # noqa: T201
    create_data = _call(
        adapter,
        "Create a ticket to add rate limiting to the public API and monitor 429s.",
    )
    ticket_id = _first_ticket_id(create_data.get("ticket_result"))
    if not ticket_id and isinstance(create_data.get("ai_result"), dict):
        candidate = create_data["ai_result"].get("ticket_id")
        ticket_id = candidate or ticket_id

    # 2) Search all tickets and pick first id if none yet
    print("\n=== SEARCH ALL ===")  # noqa: T201
    search_data = _call(adapter, "List all tickets.")
    if not ticket_id:
        ticket_id = _first_ticket_id(search_data.get("ticket_result"))

    if not ticket_id:
        print("No ticket id available; cannot continue further ops.")  # noqa: T201
        return

    # 3) Get by id
    print("\n=== GET BY ID ===")  # noqa: T201
    _call(adapter, f"Fetch the ticket with ID {ticket_id}.")

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
