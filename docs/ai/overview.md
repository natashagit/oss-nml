# AI Service Stack Overview

The AI Service Stack provides a flexible, component-based architecture for integrating AI capabilities into your application. It supports both conversational and structured output modes, making it perfect for chatbots, intent detection, and data extraction.

## Architecture

```
Consumer Code
    ↓
ai_api.get_client()
    ↓
    ├── openai_impl.OpenAIClient (Local)
    │       ↓
    │   OpenAI API
    │
    └── ai_adapter.ServiceClient (Remote)
            ↓
        ai_service_client (HTTP)
            ↓
        ai_service (FastAPI)
            ↓
        openai_impl.OpenAIClient
            ↓
        OpenAI API
```

## Components

### Core Components

1. **ai_api** - Abstract interface (ABC) defining the contract for AI operations
2. **openai_impl** - Concrete implementation using OpenAI's API
3. **ai_service** - FastAPI REST service exposing AI functionality
4. **ai_adapter** - Adapter wrapping the service client to match the interface
5. **ai_service_client** - Auto-generated HTTP client from OpenAPI spec

## Key Features

### Conversational Mode

Generate natural language responses without structured output:

```python
import openai_impl
from ai_api import get_client

client = get_client()
response = client.generate_response(
    user_input="What is 2+2?",
    system_prompt="You are a helpful math tutor."
)
print(response)
# Output: "2+2 equals 4."
```

### Structured Mode

Extract structured data using JSON Schema:

```python
from ai_api import get_client

client = get_client()

schema = {
    "name": "email_action",
    "description": "Extract email action intent",
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
    user_input="Delete email 12345",
    system_prompt="Extract the email action.",
    response_schema=schema
)
print(response)
# Output: {"action": "delete", "message_id": "12345"}
```

## Quick Start

### Local Implementation

```bash
# Set API key
export OPENAI_API_KEY="your_key"

# Run directly
python -c "
import openai_impl
from ai_api import get_client

client = get_client()
print(client.generate_response('Hello!', 'Be friendly'))
"
```

### Remote Service

```bash
# Terminal 1: Start service
export OPENAI_API_KEY="your_key"
uv run uvicorn ai_service.main:app --reload

# Terminal 2: Use adapter
python -c "
import ai_adapter
from ai_api import get_client

ai_adapter.register(base_url='http://127.0.0.1:8000')
client = get_client()
print(client.generate_response('Hello!', 'Be friendly'))
"
```

## Use Cases

### Intent Detection

Analyze user input to determine what action they want to perform:

```python
schema = {
    "name": "intent_detection",
    "description": "Detect user intent",
    "schema": {
        "type": "object",
        "properties": {
            "intent": {
                "type": "string",
                "enum": ["email_management", "weather_query", "general_conversation"]
            },
            "confidence": {"type": "number"}
        },
        "required": ["intent", "confidence"],
        "additionalProperties": False
    }
}

response = client.generate_response(
    "Show me my last 5 unread emails",
    "Analyze the user's intent.",
    response_schema=schema
)
# Output: {"intent": "email_management", "confidence": 0.95}
```

### Data Extraction

Extract structured information from natural language:

```python
schema = {
    "name": "ticket_command",
    "description": "Extract ticket information",
    "schema": {
        "type": "object",
        "properties": {
            "intent": {"type": "string"},
            "title": {"type": "string"},
            "priority": {"type": "string", "enum": ["low", "medium", "high"]}
        },
        "required": ["intent", "title"],
        "additionalProperties": False
    }
}

response = client.generate_response(
    "Create a high priority ticket to fix login redirect",
    "Extract ticket details.",
    response_schema=schema
)
# Output: {"intent": "create_ticket", "title": "Fix login redirect", "priority": "high"}
```

## Design Principles

1. **Interface-Implementation Separation** - Abstract contract separate from concrete implementation
2. **Dependency Injection** - Implementations registered at runtime
3. **Adapter Pattern** - Service client wrapped to match local interface
4. **Factory Pattern** - `get_client()` returns registered implementation
5. **Type Safety** - Full type hints throughout

## Benefits

- **Flexibility** - Switch between local and remote without code changes
- **Testability** - Easy to mock implementations
- **Scalability** - Service can be deployed and scaled independently
- **Maintainability** - Clear separation of concerns
- **Type Safety** - Full IDE support with type hints

## Next Steps

- [AI API Reference](ai_api.md) - Abstract interface documentation
- [OpenAI Implementation](openai_impl.md) - Concrete implementation details
- [AI Service](ai_service.md) - FastAPI service documentation
- [AI Adapter](ai_adapter.md) - Adapter pattern implementation
- [Testing Guide](../testing.md) - How to test AI components
