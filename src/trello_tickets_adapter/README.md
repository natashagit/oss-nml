# Trello Tickets Adapter

## Overview
`trello_tickets_adapter` provides an adapter that maps the Kanban API (from the other team) to your Tickets API, enabling Trello integration for ticket management.

## Purpose

This adapter bridges two different APIs:
- **Input**: Your `tickets_api.TicketInterface` (OPEN, IN_PROGRESS, CLOSED)
- **Output**: Other team's `kanban_client_api.KanbanClient` (Boards, Lists, Cards)
- **Backend**: Trello via their `trello_client_impl`

## Architecture

```
Your AI Ticket Service
    ↓
tickets_api.TicketInterface
    ↓
trello_tickets_adapter.TrelloTicketsClient (This package)
    ↓
kanban_client_api.KanbanClient (Other team's API)
    ↓
trello_client_impl.TrelloClientImpl (Other team's implementation)
    ↓
Trello API
```

## Status Mapping

Tickets map to Trello lists as follows:

| Ticket Status | Trello List | Description |
|---------------|-------------|-------------|
| `OPEN` | "To Do" | New tickets waiting to be started |
| `IN_PROGRESS` | "In Progress" | Tickets currently being worked on |
| `CLOSED` | "Done" | Completed tickets |

## Configuration

### Environment Variables

```bash
# Required
export TRELLO_TOKEN="your_trello_token"
export TRELLO_BOARD_ID="your_board_id"

# Optional (customize list names)
export TRELLO_TODO_LIST="To Do"
export TRELLO_IN_PROGRESS_LIST="In Progress" 
export TRELLO_DONE_LIST="Done"
```

### Getting Trello Credentials

1. **API Key**: Get from https://trello.com/app-key
2. **Token**: Generate at the same page with appropriate permissions
3. **Board ID**: Found in the Trello board URL: `https://trello.com/b/{BOARD_ID}/board-name`

## Usage

### Direct Usage

```python
from trello_tickets_adapter import TrelloTicketsClient
from tickets_api import TicketStatus

# Create client
client = TrelloTicketsClient(
    token="your_trello_token",
    board_id="your_board_id"
)

# Create ticket (goes to "To Do" list)
ticket = client.create_ticket(
    title="Fix login bug",
    description="Users cannot authenticate"
)

# Search tickets
open_tickets = client.search_tickets(status=TicketStatus.OPEN)
bug_tickets = client.search_tickets(query="bug")

# Update ticket status (moves between lists)
updated = client.update_ticket(
    ticket_id=ticket.id,
    status=TicketStatus.IN_PROGRESS
)

# Delete ticket
success = client.delete_ticket(ticket.id)
```

### Via AI Ticket Service

```bash
# Create ticket in Trello
curl -X POST http://127.0.0.1:8002/command \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Create a ticket to fix the login bug",
    "backend": "trello"
  }'

# Search Trello tickets
curl -X POST http://127.0.0.1:8002/command \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Find all tickets about bugs",
    "backend": "trello"
  }'
```

## API Reference

### TrelloTicketsClient

Implements `tickets_api.TicketInterface` using Trello as the backend.

#### Constructor

```python
TrelloTicketsClient(
    token: str,
    board_id: str,
    *,
    todo_list_name: str = "To Do",
    in_progress_list_name: str = "In Progress",
    done_list_name: str = "Done",
)
```

#### Methods

All methods from `TicketInterface`:

- `create_ticket(title, description, assignee=None) -> Ticket`
- `get_ticket(ticket_id) -> Ticket | None`
- `search_tickets(query=None, status=None) -> list[Ticket]`
- `update_ticket(ticket_id, status=None, title=None) -> Ticket`
- `delete_ticket(ticket_id) -> bool`

### TrelloTicket

Implements `tickets_api.Ticket` by wrapping Trello cards.

#### Properties

- `id: str` - Trello card ID
- `title: str` - Card name
- `description: str` - Card description
- `status: TicketStatus` - Derived from list position
- `assignee: str | None` - Always None (not implemented)

## How It Works

### List Management

The adapter automatically:
1. **Caches list IDs** for performance
2. **Creates missing lists** if they don't exist
3. **Maps statuses** to appropriate lists

### Async Handling

Since the Kanban API is async but the Ticket API is sync, the adapter:
1. **Runs async operations** in a sync context using `asyncio`
2. **Handles event loops** properly for different environments
3. **Provides sync interface** matching your existing code

### Error Handling

- **Missing lists**: Automatically created
- **Invalid tickets**: Return None or empty lists
- **API errors**: Propagated as appropriate exceptions

## Testing

```bash
# Run tests (when implemented)
uv run pytest src/trello_tickets_adapter/tests/ -v

# Test with real Trello (requires credentials)
export TRELLO_TOKEN="your_token"
export TRELLO_BOARD_ID="your_board_id"
uv run pytest src/trello_tickets_adapter/tests/ -m integration
```

## Integration with AI Ticket Service

The adapter is automatically available in the AI ticket service:

```python
# In ai_ticket_service/main.py
from trello_tickets_adapter import TrelloTicketsClient

# Factory creates the client
client = TrelloTicketsClient(token=token, board_id=board_id)

# Used exactly like Google Tasks client
ticket = client.create_ticket("Fix bug", "Description")
```

## Comparison with Google Tasks

| Feature | Google Tasks | Trello |
|---------|-------------|--------|
| **Lists** | Single tasklist | Multiple lists per board |
| **Status Mapping** | Title prefixes | List positions |
| **Assignees** | Not supported | Supported (not implemented) |
| **Rich Descriptions** | Basic notes | Full markdown support |
| **Due Dates** | Supported | Supported (not implemented) |
| **Attachments** | Not supported | Supported (not implemented) |

## Future Enhancements

Potential improvements:
1. **Assignee support** - Map to Trello card members
2. **Due date handling** - Use Trello due dates
3. **Label support** - Use Trello labels for categorization
4. **Attachment handling** - Support file attachments
5. **Webhook integration** - Real-time updates

## Dependencies

- `tickets-api` - Your ticket abstractions
- `kanban-client-api` - Other team's Kanban abstractions
- `trello-client-impl` - Other team's Trello implementation

## See Also

- [AI Ticket Service](../ai_ticket_service/README.md) - Main orchestration service
- [Tickets API](../tickets_api/README.md) - Abstract ticket interface
- [Tickets Client Impl](../tickets_client_impl/README.md) - Google Tasks implementation