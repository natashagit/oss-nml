# OpenAI Implementation

## Overview
`openai_impl` provides a concrete implementation of `ai_api.AIInterface` backed by the OpenAI API. It handles API authentication and provides methods to generate responses from OpenAI's language models.

## Purpose

This package serves as the production-ready OpenAI integration for the AI assistant system:

- **OpenAI API Integration**: Connects to OpenAI using the official Python client
- **API Key Authentication**: Handles secure authentication via API keys
- **ABC Implementation**: Provides concrete implementation of AIInterface
- **Structured Output Support**: Supports both conversational and structured responses
- **Dependency Injection**: Automatically registers itself as the AIInterface implementation

## Architecture

### Authentication
- API key authentication via environment variable `OPENAI_API_KEY`
- Credentials loaded automatically from environment

### Dependency Injection
```python
import openai_impl  # registers the implementation

from ai_api import AIInterface
# Use the registered implementation
```

## API Reference

### OpenAIClient
Implements the `ai_api.AIInterface` abstract base class.

#### Methods
- `generate_response(user_input: str, system_prompt: str, response_schema: dict[str, Any] | None = None) -> str | dict[str, Any]`: Generates a response from OpenAI's API. Returns structured data if a schema is provided, otherwise returns conversational text.

### Factory Function
`get_ai_impl() -> AIInterface`: Creates an `OpenAIClient` instance and assigns it to the AI API during import.

## Usage Examples

### Basic Usage
```python
import openai_impl
from ai_api import AIInterface

# Implementation is automatically registered
client = openai_impl.OpenAIClient()
response = client.generate_response(
    user_input="What is the weather like?",
    system_prompt="You are a helpful assistant."
)
print(response)
```

### Structured Output for Intent Detection and Tool Calling

The OpenAI implementation supports structured outputs using JSON Schema, which is perfect for analyzing user input, determining intent, and extracting structured data for tool calls.

```python
import openai_impl

client = openai_impl.OpenAIClient()

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

## Authentication Setup

### Environment Variables
```bash
export OPENAI_API_KEY="your_api_key_here"
```

### Usage
```python
import openai_impl

# API key is loaded from environment automatically
client = openai_impl.OpenAIClient()
```

## Testing
```bash
uv run pytest src/openai_impl/tests/ -q
uv run pytest src/openai_impl/tests/ --cov=src/openai_impl --cov-report=term-missing
```
