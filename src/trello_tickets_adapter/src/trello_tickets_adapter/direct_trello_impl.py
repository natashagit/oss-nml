"""Direct Trello implementation using their client."""

import asyncio
import logging
import os
from typing import Any

from tickets_api import Ticket as TicketABC
from tickets_api import TicketInterface, TicketStatus

from trello_tickets_adapter.ticket_impl import TrelloTicket


class DirectTrelloClient(TicketInterface):
    """Direct Trello client that bypasses the Kanban API."""

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
        """Initialize the direct Trello client."""
        self.logger = logging.getLogger(__name__)
        self.board_id = board_id
        self.token = token
        self.api_key = api_key
        
        # Set environment variables for their client
        os.environ['TRELLO_API_KEY'] = api_key
        os.environ['TRELLO_API_SECRET'] = api_secret
        os.environ['TRELLO_TOKEN'] = token
        os.environ['REDIRECT_URI'] = 'http://localhost:8000/callback'
        
        # Import and create their client directly
        import trello_client_impl  # noqa: F401
        from trello_client_impl.trello_impl import TrelloClientImpl
        
        self.trello_client = TrelloClientImpl(token=token)
        
        # List name mappings
        self.status_to_list_name = {
            TicketStatus.OPEN: todo_list_name,
            TicketStatus.IN_PROGRESS: in_progress_list_name,
            TicketStatus.CLOSED: done_list_name,
        }
        
        # Cache for list IDs
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
        
        lists = await self.trello_client.get_lists(self.board_id)
        for trello_list in lists:
            if trello_list.name == list_name:
                self._list_id_cache[list_name] = trello_list.id
                return trello_list.id
        
        # If list doesn't exist, create it
        self.logger.info("Creating list '%s' in board %s", list_name, self.board_id)
        new_list = await self.trello_client.create_list(self.board_id, list_name)
        self._list_id_cache[list_name] = new_list.id
        return new_list.id

    def create_ticket(self, title: str, description: str, assignee: str | None = None) -> TicketABC:
        """Create a new ticket in the 'To Do' list."""
        return self._run_async(self._create_ticket_async(title, description, assignee))

    async def _create_ticket_async(self, title: str, description: str, assignee: str | None) -> TicketABC:
        """Async implementation of create_ticket."""
        # Get the "To Do" list ID
        list_id = await self._get_list_id_by_name(self.status_to_list_name[TicketStatus.OPEN])
        
        # Create the card
        card = await self.trello_client.create_card(
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
            card = await self.trello_client.get_card(ticket_id)
            # Determine status from list
            lists = await self.trello_client.get_lists(self.board_id)
            status = TicketStatus.OPEN  # Default
            
            for trello_list in lists:
                if trello_list.id == card.list_id:
                    for ticket_status, list_name in self.status_to_list_name.items():
                        if trello_list.name == list_name:
                            status = ticket_status
                            break
                    break
            
            return TrelloTicket(card, status)
        except Exception:
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
        
        # Get all lists
        lists = await self.trello_client.get_lists(self.board_id)
        
        # Filter lists by status if specified
        lists_to_search = []
        if status is not None:
            target_list_name = self.status_to_list_name[status]
            for trello_list in lists:
                if trello_list.name == target_list_name:
                    lists_to_search.append(trello_list)
        else:
            lists_to_search = lists

        # Search cards in the selected lists
        for trello_list in lists_to_search:
            cards = await self.trello_client.get_cards(trello_list.id)
            
            # Determine status for this list
            list_status = TicketStatus.OPEN  # Default
            for ticket_status, list_name in self.status_to_list_name.items():
                if trello_list.name == list_name:
                    list_status = ticket_status
                    break
            
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
        card = await self.trello_client.get_card(ticket_id)
        
        # Determine new list ID if status is changing
        new_list_id = None
        if status is not None:
            list_name = self.status_to_list_name[status]
            new_list_id = await self._get_list_id_by_name(list_name)
        
        # Update the card
        updated_card = await self.trello_client.update_card(
            card_id=ticket_id,
            name=title,
            list_id=new_list_id,
        )
        
        # Determine final status
        final_status = status if status is not None else TicketStatus.OPEN
        
        return TrelloTicket(updated_card, final_status)

    def delete_ticket(self, ticket_id: str) -> bool:
        """Delete a ticket."""
        return self._run_async(self._delete_ticket_async(ticket_id))

    async def _delete_ticket_async(self, ticket_id: str) -> bool:
        """Async implementation of delete_ticket."""
        try:
            return await self.trello_client.delete_card(ticket_id)
        except Exception:
            return False