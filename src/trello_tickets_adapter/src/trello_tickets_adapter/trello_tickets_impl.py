"""Adapter that maps Trello Kanban API to Tickets API."""

import asyncio
import logging
from typing import Any

from kanban_client_api import get_client as get_kanban_client
from kanban_client_api.models import KanbanCard, KanbanList
from tickets_api import Ticket as TicketABC
from tickets_api import TicketInterface, TicketStatus

from trello_tickets_adapter.ticket_impl import TrelloTicket

# Import trello implementation to register it globally
import trello_client_impl  # noqa: F401

# Register the trello client implementation
trello_client_impl.register()


class TrelloTicketsClient(TicketInterface):
    """Adapter that implements TicketInterface using Trello via Kanban API."""

    def __init__(
        self,
        token: str,
        board_id: str,
        api_key: str,
        api_secret: str,
        *,
        todo_list_name: str = "To Do",
        in_progress_list_name: str = "In Progress", 
        done_list_name: str = "Done",
    ) -> None:
        """Initialize the Trello tickets client.

        Args:
            token: Trello API token
            board_id: ID of the Trello board to use for tickets
            api_key: Trello API key
            api_secret: Trello API secret
            todo_list_name: Name of the list for OPEN tickets
            in_progress_list_name: Name of the list for IN_PROGRESS tickets
            done_list_name: Name of the list for CLOSED tickets
        """
        import os
        self.logger = logging.getLogger(__name__)
        self.board_id = board_id
        
        # Set environment variables that the Trello client expects
        os.environ['TRELLO_API_KEY'] = api_key
        os.environ['TRELLO_API_SECRET'] = api_secret
        os.environ['TRELLO_TOKEN'] = token
        os.environ['REDIRECT_URI'] = 'http://localhost:8000/callback'  # Default for their OAuth
        
        # Create TrelloClientImpl directly instead of using get_kanban_client
        from trello_client_impl.trello_impl import TrelloClientImpl
        self.kanban_client = TrelloClientImpl(token=token)
        
        # List name mappings
        self.status_to_list_name = {
            TicketStatus.OPEN: todo_list_name,
            TicketStatus.IN_PROGRESS: in_progress_list_name,
            TicketStatus.CLOSED: done_list_name,
        }
        
        # Cache for list IDs (populated on first use)
        self._list_id_cache: dict[str, str] = {}

    def _run_async(self, coro: Any) -> Any:
        """Run async coroutine in sync context."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro)

    async def _get_list_id_by_name(self, list_name: str) -> str:
        """Get list ID by name, with caching."""
        if list_name in self._list_id_cache:
            return self._list_id_cache[list_name]
        
        lists = await self.kanban_client.get_lists(self.board_id)
        for kanban_list in lists:
            if kanban_list.name == list_name:
                self._list_id_cache[list_name] = kanban_list.id
                return kanban_list.id
        
        # If list doesn't exist, create it
        self.logger.info("Creating list '%s' in board %s", list_name, self.board_id)
        new_list = await self.kanban_client.create_list(self.board_id, list_name)
        self._list_id_cache[list_name] = new_list.id
        return new_list.id

    async def _get_list_name_by_id(self, list_id: str) -> str:
        """Get list name by ID."""
        # Check cache first (reverse lookup)
        for name, cached_id in self._list_id_cache.items():
            if cached_id == list_id:
                return name
        
        # Fetch from API
        lists = await self.kanban_client.get_lists(self.board_id)
        for kanban_list in lists:
            self._list_id_cache[kanban_list.name] = kanban_list.id
            if kanban_list.id == list_id:
                return kanban_list.name
        
        return "Unknown"

    def _list_name_to_status(self, list_name: str) -> TicketStatus:
        """Convert list name to ticket status."""
        for status, name in self.status_to_list_name.items():
            if name == list_name:
                return status
        
        # Default to OPEN for unknown lists
        return TicketStatus.OPEN

    def create_ticket(self, title: str, description: str, assignee: str | None = None) -> TicketABC:
        """Create a new ticket in the 'To Do' list."""
        return self._run_async(self._create_ticket_async(title, description, assignee))

    async def _create_ticket_async(self, title: str, description: str, assignee: str | None) -> TicketABC:
        """Async implementation of create_ticket."""
        # Get the "To Do" list ID
        list_id = await self._get_list_id_by_name(self.status_to_list_name[TicketStatus.OPEN])
        
        # Create the card
        card = await self.kanban_client.create_card(
            list_id=list_id,
            name=title,
            description=description or ""
        )
        
        return TrelloTicket(card, TicketStatus.OPEN)

    def get_ticket(self, ticket_id: str) -> TicketABC | None:
        """Retrieve a ticket by its ID."""
        return self._run_async(self._get_ticket_async(ticket_id))

    async def _get_ticket_async(self, ticket_id: str) -> TicketABC | None:
        """Async implementation of get_ticket."""
        try:
            card = await self.kanban_client.get_card(ticket_id)
            list_name = await self._get_list_name_by_id(card.list_id)
            status = self._list_name_to_status(list_name)
            return TrelloTicket(card, status)
        except Exception:
            # Card not found or other error
            return None

    def search_tickets(
        self, 
        query: str | None = None, 
        status: TicketStatus | None = None
    ) -> list[TicketABC]:
        """Search for tickets based on query and/or status."""
        return self._run_async(self._search_tickets_async(query, status))

    async def _search_tickets_async(
        self, 
        query: str | None, 
        status: TicketStatus | None
    ) -> list[TicketABC]:
        """Async implementation of search_tickets."""
        matching_tickets: list[TicketABC] = []
        
        # Get lists to search
        lists_to_search: list[KanbanList] = []
        if status is not None:
            # Search only the specific status list
            list_name = self.status_to_list_name[status]
            list_id = await self._get_list_id_by_name(list_name)
            all_lists = await self.kanban_client.get_lists(self.board_id)
            for kanban_list in all_lists:
                if kanban_list.id == list_id:
                    lists_to_search.append(kanban_list)
                    break
        else:
            # Search all lists
            lists_to_search = await self.kanban_client.get_lists(self.board_id)

        # Search cards in the selected lists
        for kanban_list in lists_to_search:
            cards = await self.kanban_client.get_cards(kanban_list.id)
            list_status = self._list_name_to_status(kanban_list.name)
            
            for card in cards:
                # Filter by query if provided
                if query is not None:
                    query_lower = query.lower()
                    title_match = query_lower in card.name.lower()
                    description_match = query_lower in (card.description or "").lower()
                    if not (title_match or description_match):
                        continue
                
                matching_tickets.append(TrelloTicket(card, list_status))

        return matching_tickets

    def update_ticket(
        self,
        ticket_id: str,
        status: TicketStatus | None = None,
        title: str | None = None,
    ) -> TicketABC:
        """Update a ticket's details."""
        return self._run_async(self._update_ticket_async(ticket_id, status, title))

    async def _update_ticket_async(
        self,
        ticket_id: str,
        status: TicketStatus | None,
        title: str | None,
    ) -> TicketABC:
        """Async implementation of update_ticket."""
        # Get current card
        card = await self.kanban_client.get_card(ticket_id)
        
        # Determine new list ID if status is changing
        new_list_id = None
        if status is not None:
            list_name = self.status_to_list_name[status]
            new_list_id = await self._get_list_id_by_name(list_name)
        
        # Update the card
        updated_card = await self.kanban_client.update_card(
            card_id=ticket_id,
            name=title,
            list_id=new_list_id,
        )
        
        # Determine final status
        final_list_name = await self._get_list_name_by_id(updated_card.list_id)
        final_status = self._list_name_to_status(final_list_name)
        
        return TrelloTicket(updated_card, final_status)

    def delete_ticket(self, ticket_id: str) -> bool:
        """Delete a ticket."""
        return self._run_async(self._delete_ticket_async(ticket_id))

    async def _delete_ticket_async(self, ticket_id: str) -> bool:
        """Async implementation of delete_ticket."""
        try:
            return await self.kanban_client.delete_card(ticket_id)
        except Exception:
            return False