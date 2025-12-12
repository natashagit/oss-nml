"""Quick integration script: exercise the ticketing client directly."""

import logging
import os

from dotenv import load_dotenv
from tickets_client_impl import TicketsClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()


def main() -> None:
    """Create a sample ticket using the ticket client implementation."""
    interactive = os.getenv("TASKS_INTERACTIVE", "false").lower() == "true"
    client = TicketsClient(interactive=interactive)
    ticket = client.create_ticket(
        title="Integration test ticket",
        description="Created via integrate.py direct call.",
    )
    logger.info(
        "Ticket created: id=%s title=%s status=%s",
        ticket.id,
        ticket.title,
        getattr(ticket.status, "value", ticket.status),
    )


if __name__ == "__main__":
    main()
