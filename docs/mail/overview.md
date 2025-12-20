# Mail Client Stack Overview

The Mail Client Stack provides a flexible, component-based architecture for integrating email functionality into your application using the Gmail API.

## Architecture

```
Consumer Code
    ↓
mail_client_api.get_client()
    ↓
    ├── gmail_client_impl.GmailClient (Local)
    │       ↓
    │   Gmail API
    │
    └── mail_client_adapter.ServiceClient (Remote)
            ↓
        mail_client_service_client (HTTP)
            ↓
        mail_client_service (FastAPI)
            ↓
        gmail_client_impl.GmailClient
            ↓
        Gmail API
```

## Components

### Core Components

1. **mail_client_api** - Abstract interface (ABC) defining the contract for mail operations
2. **gmail_client_impl** - Concrete implementation using Gmail API
3. **mail_client_service** - FastAPI REST service exposing mail functionality
4. **mail_client_adapter** - Adapter wrapping the service client to match the interface
5. **mail_client_service_client** - Auto-generated HTTP client from OpenAPI spec

## Key Features

- **Message Listing** - Fetch multiple messages
- **Message Retrieval** - Get single message details
- **Mark as Read** - Update message status
- **Delete** - Remove messages

## Quick Start

### Local Implementation

```bash
# Set up credentials (see setup guide)
# Place credentials.json in project root

# Run directly
python -c "
import gmail_client_impl
from mail_client_api import get_client

client = get_client()
messages = client.get_messages(max_results=5)
for msg in messages:
    print(f'{msg.id}: {msg.subject}')
"
```

### Remote Service

```bash
# Terminal 1: Start service
uv run uvicorn mail_client_service.main:app --reload --port 8001

# Terminal 2: Use adapter
python -c "
import mail_client_adapter
from mail_client_api import get_client

mail_client_adapter.register(base_url='http://127.0.0.1:8001')
client = get_client()
messages = client.get_messages(max_results=5)
for msg in messages:
    print(f'{msg.id}: {msg.subject}')
"
```

## Design Principles

1. **Interface-Implementation Separation** - Abstract contract separate from concrete implementation
2. **Dependency Injection** - Implementations registered at runtime
3. **Adapter Pattern** - Service client wrapped to match local interface
4. **Factory Pattern** - `get_client()` returns registered implementation
5. **Type Safety** - Full type hints throughout

## See Also

- [Mail Client API Reference](../api/mail_client_api.md) - Abstract interface
- [Gmail Client Implementation](../api/gmail_client_impl.md) - Concrete implementation
- [Testing Guide](../testing.md) - How to test mail components
