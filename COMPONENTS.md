# Component Documentation Index

This document provides a quick reference to all components in the project and their documentation.

## AI Service Stack

### Core Components

| Component | Purpose | README |
|-----------|---------|--------|
| **ai_api** | Abstract AI interface (ABC) | [src/ai_api/README.md](src/ai_api/README.md) |
| **openai_impl** | OpenAI implementation | [src/openai_impl/README.md](src/openai_impl/README.md) |
| **ai_service** | FastAPI REST service | [src/ai_service/README.md](src/ai_service/README.md) |
| **ai_adapter** | Service client adapter | [src/ai_adapter/README.md](src/ai_adapter/README.md) |
| **ai_service_client** | Auto-generated HTTP client | [src/ai_service_client/README.md](src/ai_service_client/README.md) |

## AI Ticket Service Stack

### Core Components

| Component | Purpose | README |
|-----------|---------|--------|
| **ai_ticket_service** | AI-powered ticket orchestration | [src/ai_ticket_service/README.md](src/ai_ticket_service/README.md) |
| **tickets_api** | Abstract ticket interface (ABC) | [src/tickets_api/README.md](src/tickets_api/README.md) |
| **tickets_client_impl** | Google Tasks implementation | [src/tickets_client_impl/README.md](src/tickets_client_impl/README.md) |
| **trello_tickets_adapter** | Trello implementation (via Kanban API) | [src/trello_tickets_adapter/README.md](src/trello_tickets_adapter/README.md) |

### Quick Start

```bash
# Set API key
export OPENAI_API_KEY="your_key"

# Start service
uv run uvicorn ai_service.main:app --reload

# Run demo
uv run python main.py
```

### Quick Start (Ticket Service)

```bash
# Set credentials
export OPENAI_API_KEY="your_key"
export TRELLO_TOKEN="your_trello_token"
export TRELLO_BOARD_ID="your_board_id"

# Start ticket service
uv run uvicorn ai_ticket_service.main:app --reload --port 8002

# Run multi-backend demo
uv run python example_multi_backend.py
```

## Mail Client Stack

### Core Components

| Component | Purpose | README |
|-----------|---------|--------|
| **mail_client_api** | Abstract mail client interface (ABC) | [src/mail_client_api/README.md](src/mail_client_api/README.md) |
| **gmail_client_impl** | Gmail implementation | [src/gmail_client_impl/README.md](src/gmail_client_impl/README.md) |
| **mail_client_service** | FastAPI REST service | [src/mail_client_service/README.md](src/mail_client_service/README.md) |
| **mail_client_adapter** | Service client adapter | [src/mail_client_adapter/README.md](src/mail_client_adapter/README.md) |
| **mail_client_service_client** | Auto-generated HTTP client | [src/mail_client_service_client/README.md](src/mail_client_service_client/README.md) |

### Quick Start

```bash
# Set up credentials (see README)
# Place credentials.json in project root

# Start service
uv run uvicorn mail_client_service.main:app --reload --port 8001
```

## Architecture Pattern

Both stacks follow the same architectural pattern:

```
Consumer Code
    ↓
Abstract API (get_client)
    ↓
    ├── Local Implementation (Direct API)
    │       ↓
    │   External API (OpenAI/Gmail)
    │
    └── Adapter (Remote Service)
            ↓
        Service Client (HTTP)
            ↓
        FastAPI Service
            ↓
        Local Implementation
            ↓
        External API
```

## Key Features by Component

### AI Stack Features

- **Conversational Mode**: Natural language responses
- **Structured Mode**: JSON output matching provided schema
- **Intent Detection**: Extract structured data from user input
- **Seamless Switching**: Same code for local or remote

### Mail Stack Features

- **Message Listing**: Fetch multiple messages
- **Message Retrieval**: Get single message details
- **Mark as Read**: Update message status
- **Delete**: Remove messages

## Documentation Structure

Each component README includes:

1. **Overview**: What the component does
2. **Purpose**: Why it exists
3. **Installation**: How to set it up
4. **Usage Examples**: Code samples with input/output
5. **API Reference**: Methods and parameters
6. **Configuration**: Environment variables and settings
7. **Testing**: How to run tests
8. **Integration**: How it connects to other components

## Running Examples

### AI Service Examples

#### Conversational (No Schema)

```python
import openai_impl
from ai_api import get_client

client = get_client()
response = client.generate_response(
    "What is 2+2?",
    "You are a math tutor."
)
print(response)
# Output: "2+2 equals 4."
```

#### Structured (With Schema)

```python
import openai_impl
from ai_api import get_client

client = get_client()

schema = {
    "name": "email_action",
    "description": "Extract email action",
    "schema": {
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["delete", "mark_as_read"]},
            "message_id": {"type": "string"}
        },
        "required": ["action"],
        "additionalProperties": False
    }
}

response = client.generate_response(
    "Delete email 12345",
    "Extract the action.",
    response_schema=schema
)
print(response)
# Output: {"action": "delete", "message_id": "12345"}
```

#### Remote Service (via Adapter)

```python
import ai_adapter
from ai_api import get_client

# Register adapter to use remote service
ai_adapter.register(base_url="http://127.0.0.1:8000")

client = get_client()
response = client.generate_response(
    "Say hello in 3 words",
    "You are concise."
)
print(response)
# Output: "Hello there friend!"
```

## Testing

```bash
# Run all tests
uv run pytest

# Run AI stack tests only
uv run pytest src/ai_api src/ai_service src/ai_adapter src/openai_impl -v

# Run mail stack tests only
uv run pytest src/mail_client_api src/mail_client_service -v

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing
```

## Development Workflow

1. **Install dependencies**: `uv sync --all-packages --extra dev`
2. **Run tests**: `uv run pytest -v`
3. **Check code quality**: `uv run ruff check . && uv run ruff format --check .`
4. **Fix formatting**: `uv run ruff format .`
5. **Type checking**: `uv run mypy src tests`
6. **View docs**: `uv run mkdocs serve`

## API Documentation

When services are running, access interactive API docs:

- **AI Service**: http://127.0.0.1:8000/docs
- **Mail Service**: http://127.0.0.1:8001/docs

## Environment Variables

### AI Service

```bash
export OPENAI_API_KEY="your_openai_api_key"
export AI_SERVICE_URL="http://127.0.0.1:8000"  # Optional
```

### Mail Service

```bash
export GMAIL_CLIENT_ID="your_client_id"
export GMAIL_CLIENT_SECRET="your_client_secret"
export GMAIL_REFRESH_TOKEN="your_refresh_token"
```

Or use credential files:
- `credentials.json` - OAuth credentials
- `token.json` - Generated after first auth

## Design Principles

1. **Interface-Implementation Separation**: Abstract contracts (ABC) separate from concrete implementations
2. **Dependency Injection**: Implementations registered at runtime via `register()` functions
3. **Adapter Pattern**: Service clients wrapped to match local interface
4. **Factory Pattern**: `get_client()` functions return registered implementations
5. **OpenAPI Standard**: Auto-generated clients from service specifications

## Benefits

- **Testability**: Easy to mock implementations
- **Flexibility**: Switch between local and remote without code changes
- **Scalability**: Services can be deployed and scaled independently
- **Maintainability**: Clear separation of concerns
- **Reusability**: Components can be used in other projects
- **Type Safety**: Full type hints throughout

## Next Steps

1. Read the [main README](README.md) for project overview
2. Explore individual component READMEs for detailed documentation
3. Run the examples to see the system in action
4. Check the [docs/](docs/) directory for additional documentation
5. Review tests for more usage examples
