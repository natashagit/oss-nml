# Tickets API

Abstract interface definitions for ticketing systems. This package provides the core contracts (abstract base classes) that all ticket backend implementations must follow.

## Overview

The Tickets API defines a uniform interface for interacting with different ticketing backends (Google Tasks, Trello, Jira, etc.) without coupling to any specific implementation.

## Core Components

### `Ticket` (Abstract Base Class)
Represents a ticket with the following properties:
- `id`: Unique identifier
- `title`: Ticket title
- `description`: Detailed description
- `status`: Current status (see `TicketStatus`)
- `assignee`: Assigned user ID (optional)

### `TicketStatus` (Enum)
Possible ticket statuses:
- `OPEN`: Ticket is open and not started
- `IN_PROGRESS`: Work is in progress
- `CLOSED`: Ticket is completed/resolved

### `TicketInterface` (Abstract Base Class)
The contract for ticketing services with these operations:

#### `create_ticket(title, description, assignee=None) -> Ticket`
Create a new ticket.

#### `get_ticket(ticket_id) -> Ticket | None`
Retrieve a ticket by ID. Returns `None` if not found.

#### `search_tickets(query=None, status=None) -> list[Ticket]`
Search tickets by text query and/or status filter.

#### `update_ticket(ticket_id, status=None, title=None) -> Ticket`
Update ticket properties. Only provided fields are updated.

#### `delete_ticket(ticket_id) -> bool`
Delete a ticket. Returns `True` if successful.

## Usage

This package is meant to be implemented by concrete ticket backend packages:
- `tickets_client_impl` - Google Tasks implementation
- `trello_ticket_impl` - Trello implementation
- Others can be added by implementing `TicketInterface`

Example implementation structure:
```python
from tickets_api import Ticket, TicketInterface, TicketStatus

class MyTicketBackend(TicketInterface):
    def create_ticket(self, title: str, description: str, assignee: str | None = None) -> Ticket:
        # Implementation here
        pass

    # ... implement other methods
```

## Benefits

- **Backend Independence**: Swap ticket backends without changing application code
- **Type Safety**: Well-defined interfaces with type hints
- **Consistency**: All backends follow the same contract
