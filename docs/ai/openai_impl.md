# OpenAI Implementation

The `openai_impl` package provides a concrete implementation of the `ai_api.AIInterface` using OpenAI's API.

## Overview

This package serves as the production-ready OpenAI integration:

- **OpenAI API Integration** - Uses the official OpenAI Python client
- **API Key Authentication** - Secure authentication via environment variables
- **Structured Output** - Supports JSON Schema for structured responses
- **Auto-Registration** - Automatically registers itself on import

## OpenAIClient

::: openai_impl.OpenAIClient
    options:
      show_source: false
      members:
        - __init__
        - generate_response

## Quick Start

### Basic Usage

```python
import openai_impl
from ai_api import get_client

# Implementation is automatically registered on import
client = get_client()

# Simple conversational response
response = client.generate_response(
    user_input="What is 2+2?",
    system_prompt="You are a helpful math tutor."
)
print(response)  # "2+2 equals 4."
```

### Direct Client Usage

```python
import openai_impl

# Create client directly
client = openai_impl.OpenAIClient()

response = client.generate_response(
    user_input="Explain Python decorators in one sentence.",
    system_prompt="You are concise and clear."
)
print(response)
```

## Structured Output Examples

### Intent Detection

```python
import openai_impl
from ai_api import get_client

client = get_client()

# Define a schema for email action intent detection
email_action_schema = {
    "name": "email_action",
    "description": "Extract email action intent and parameters from user input",
    "schema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["delete", "mark_as_read", "get_message", "list_messages"],
                "description": "The email action the user wants to perform"
            },
            "message_id": {
                "type": "string",
                "description": "The ID of the message to act upon (if applicable)"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of messages to retrieve (for list_messages)"
            }
        },
        "required": ["action"],
        "additionalProperties": False
    }
}

# User says: "Delete the email with ID 12345"
response = client.generate_response(
    user_input="Delete the email with ID 12345",
    system_prompt="You are an AI that extracts email action intents from user requests.",
    response_schema=email_action_schema
)

print(response)
# Output: {"action": "delete", "message_id": "12345"}
```

### Multi-Intent Detection

```python
from ai_api import get_client

client = get_client()

# Schema for detecting multiple possible actions
multi_action_schema = {
    "name": "intent_detection",
    "description": "Detect user intent and extract relevant parameters",
    "schema": {
        "type": "object",
        "properties": {
            "intent": {
                "type": "string",
                "enum": ["email_management", "weather_query", "calendar_event", "general_conversation"]
            },
            "confidence": {
                "type": "number",
                "description": "Confidence score between 0 and 1"
            },
            "parameters": {
                "type": "object",
                "description": "Intent-specific parameters",
                "additionalProperties": True
            }
        },
        "required": ["intent", "confidence"],
        "additionalProperties": False
    }
}

response = client.generate_response(
    user_input="Show me my last 5 unread emails",
    system_prompt="Analyze the user's intent and extract relevant parameters.",
    response_schema=multi_action_schema
)

print(response)
# Output: {
#   "intent": "email_management",
#   "confidence": 0.95,
#   "parameters": {
#     "action": "list_messages",
#     "filter": "unread",
#     "count": 5
#   }
# }
```

### Ticket Creation

```python
from ai_api import get_client

client = get_client()

ticket_schema = {
    "name": "ticket_command",
    "description": "Extract intent and title from a ticket request",
    "schema": {
        "type": "object",
        "properties": {
            "intent": {"type": "string"},
            "title": {"type": "string"},
        },
        "required": ["intent", "title"],
        "additionalProperties": False,
    },
}

result = client.generate_response(
    user_input="Create a ticket to fix login redirect.",
    system_prompt="Extract intent and title fields.",
    response_schema=ticket_schema,
)
print(result)
# Output: {"intent": "create_ticket", "title": "Fix login redirect"}
```

## Configuration

### Environment Variables

```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

### .env File

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Programmatic Configuration

```python
import openai_impl

# Pass API key directly
client = openai_impl.OpenAIClient(api_key="your_api_key_here")

# Or register with custom key
openai_impl.register(api_key="your_api_key_here")
```

### Model Selection

```python
import openai_impl

# Use default model (gpt-4o-mini)
client = openai_impl.OpenAIClient()

# Use custom model
client = openai_impl.OpenAIClient(model="gpt-4")
```

## Error Handling

```python
import openai_impl
from ai_api import get_client

try:
    client = get_client()
    response = client.generate_response("Hello", "Be helpful")
except RuntimeError as e:
    print(f"Error: {e}")
```

## Response Schema Format

The `response_schema` parameter should follow this structure:

```python
{
    "name": "schema_name",           # Name of the schema
    "description": "What it does",   # Description
    "schema": {                      # JSON Schema specification
        "type": "object",
        "properties": {
            "field1": {"type": "string"},
            "field2": {"type": "integer"}
        },
        "required": ["field1"],
        "additionalProperties": False  # Recommended for strict mode
    }
}
```

## Testing

```bash
# Run unit tests
uv run pytest src/openai_impl/tests/ -v

# Run with coverage
uv run pytest src/openai_impl/tests/ --cov=src/openai_impl --cov-report=term-missing
```

## Integration

- **ai_api** - Implements the `AIInterface` contract
- **ai_service** - Uses this implementation to process requests
- **ai_adapter** - Alternative implementation that calls the service remotely

## Performance

- **Model**: Uses `gpt-4o-mini` by default (fast and cost-effective)
- **Structured Output**: Uses OpenAI's native structured output mode
- **Strict Mode**: Enables strict JSON schema validation
- **Error Handling**: Comprehensive error handling with clear messages

## Security

- Never commit API keys to version control
- Use environment variables or secrets management
- Rotate API keys regularly
- Monitor API usage and set spending limits

## Troubleshooting

### "No OpenAI API key found"

```bash
# Set the environment variable
export OPENAI_API_KEY="your_key_here"

# Or create a .env file
echo "OPENAI_API_KEY=your_key_here" > .env
```

### "Failed to authenticate with OpenAI"

- Verify your API key is valid
- Check your OpenAI account status
- Ensure you have sufficient credits

## See Also

- [AI API Reference](ai_api.md) - Abstract interface
- [AI Service](ai_service.md) - REST service wrapper
- [AI Adapter](ai_adapter.md) - Remote service adapter
