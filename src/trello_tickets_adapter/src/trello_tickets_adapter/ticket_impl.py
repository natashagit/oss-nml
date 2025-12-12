"""Ticket implementation that wraps Trello Kanban cards."""

from kanban_client_api.models import KanbanCard
from tickets_api import Ticket as TicketABC
from tickets_api import TicketStatus


class TrelloTicket(TicketABC):
    """Concrete implementation of Ticket using Trello Kanban cards."""

    def __init__(self, card: KanbanCard, status: TicketStatus) -> None:
        """Initialize a TrelloTicket from a KanbanCard.

        Args:
            card: The underlying KanbanCard object from Trello.
            status: The ticket status (derived from list position).
        """
        self._card = card
        self._status = status

    @property
    def id(self) -> str:
        """Unique identifier for the ticket."""
        return self._card.id

    @property
    def title(self) -> str:
        """The title of the ticket."""
        return self._card.name

    @property
    def description(self) -> str:
        """The detailed description of the ticket."""
        return self._card.description or ""

    @property
    def status(self) -> TicketStatus:
        """The current status of the ticket."""
        return self._status

    @property
    def assignee(self) -> str | None:
        """The ID of the user assigned to the ticket, if any."""
        # Trello cards can have members, but for simplicity we'll return None
        # This could be enhanced to return the first member if needed
        return None