# AI Client Adapter

Service client adapter that implements the AI client API using the generated service client. This package provides location transparency, allowing the same code to work with either local or remote AI client implementations.

## Overview

This package provides:
- **ServiceClient**: Adapter that wraps the generated AI service client
- **Location Transparency**: Same interface whether using local or remote AI client
- **Network Abstraction**: Hides HTTP details from the consumer
- **Type Safety**: Uses the same type-safe dataclasses as the API

## Architecture

The adapter implements the `ai_client_api.Client` interface by:
1. Converting API calls to HTTP requests to the AI service
2. Handling authentication via session cookies
3. Transforming responses back to the expected format
4. Providing streaming support for chat completions
5. Maintaining type safety with dataclasses

## Setup

### Prerequisites

1. The AI service must be running and accessible
2. The service client must be generated using `openapi-python-client`
3. Users must complete OAuth flow and set API key via the service

### Installation

```bash
# Install dependencies
uv sync --all-packages --extra dev

# Or manually
pip install -e src/ai_client_api
pip install -e src/ai_client_service_client  # Generated client
pip install -e src/ai_client_adapter
```

### Generating the Service Client

First, start the AI service:

```bash
uv run uvicorn ai_client_service.main:app --host 127.0.0.1 --port 8000
```

Then generate the service client:

```bash
uv run openapi-python-client generate \
    --url http://127.0.0.1:8000/openapi.json \
    --output src/ai_client_service_client
```

## Usage

### Basic Usage with Registration

```python
from ai_client_adapter import register
import ai_client_api
from ai_client_api.models import ChatMessage

# Register the service adapter
# This makes get_client() return ServiceClient instances
register(base_url="http://127.0.0.1:8000")

# Get client (will use the service adapter)
client = ai_client_api.get_client(user_id="user123")

# Generate a chat completion
messages = [
    ChatMessage(role="user", content="What is the capital of France?")
]
response = client.chat_completion(messages, model="gpt-3.5-turbo")
print(response.message.content)
print(f"Tokens used: {response.usage.total_tokens}")

# Stream a chat completion
for chunk in client.chat_completion_stream(messages, model="gpt-3.5-turbo"):
    if chunk.content:
        print(chunk.content, end="", flush=True)
```

### Direct Usage

```python
from ai_client_adapter import ServiceClient
from ai_client_api.models import ChatMessage

# Create adapter pointing to the AI service
client = ServiceClient(
    base_url="http://127.0.0.1:8000",
    user_id="user123"
)

# Generate a chat completion
messages = [
    ChatMessage(role="user", content="Hello!")
]
response = client.chat_completion(messages, model="gpt-3.5-turbo")
print(response.message.content)
```

### Integration with Existing Code

The adapter can be used as a drop-in replacement for the local AI client:

```python
from ai_client_api import get_client
from ai_client_api.models import ChatMessage

# Register local implementation
import openai_client_impl
openai_client_impl.register()

# Local usage
local_client = get_client(user_id="user123")

# Register service adapter
from ai_client_adapter import register
register(base_url="https://your-ai-service.com")

# Remote usage (same interface!)
remote_client = get_client(user_id="user123")

# Both clients have the same interface
messages = [ChatMessage(role="user", content="Hello!")]
response1 = local_client.chat_completion(messages)
response2 = remote_client.chat_completion(messages)
```

## API Reference

### ServiceClient

#### `__init__(base_url: str, user_id: str)`

Initialize the service client adapter.

**Parameters:**
- `base_url`: Base URL of the AI service (e.g., "http://127.0.0.1:8000")
- `user_id`: User ID for authentication context

#### `chat_completion(messages: list[ChatMessage], model: str, temperature: float, max_tokens: int | None) -> ChatCompletionResponse`

Generate a chat completion.

**Parameters:**
- `messages`: List of `ChatMessage` dataclass instances
- `model`: AI model to use (default: "gpt-3.5-turbo")
- `temperature`: Sampling temperature (default: 0.7)
- `max_tokens`: Maximum tokens to generate (optional)

**Returns:**
- `ChatCompletionResponse` dataclass containing the completion response

#### `chat_completion_stream(messages: list[ChatMessage], model: str, temperature: float, max_tokens: int | None) -> Iterator[ChatCompletionChunk]`

Generate a streaming chat completion.

**Parameters:**
- `messages`: List of `ChatMessage` dataclass instances
- `model`: AI model to use (default: "gpt-3.5-turbo")
- `temperature`: Sampling temperature (default: 0.7)
- `max_tokens`: Maximum tokens to generate (optional)

**Yields:**
- `ChatCompletionChunk` dataclass instances as they're generated

### register()

Register the service adapter globally so `ai_client_api.get_client()` returns `ServiceClient` instances.

```python
from ai_client_adapter import register

register(base_url="http://127.0.0.1:8000")
```

## Authentication

**Important**: The service adapter requires users to:
1. Complete OAuth flow via the service (`/oauth/authorize`)
2. Set their OpenAI API key via `POST /api-keys`
3. Maintain the session cookie for subsequent requests

The adapter handles session cookies automatically when making requests, but the OAuth flow must be completed in a browser first.

## Testing

```bash
# Run tests
uv run pytest src/ai_client_adapter/tests/

# Run with coverage
uv run pytest src/ai_client_adapter/tests/ --cov=ai_client_adapter
```

## Development

### Code Quality

```bash
# Run linting
uv run ruff check src/ai_client_adapter/

# Run type checking
uv run mypy src/ai_client_adapter/
```

## Notes

- The adapter requires the generated service client to be available
- All network requests are synchronous (async support can be added if needed)
- Error handling follows the same patterns as the local implementation
- The adapter maintains the same interface as the original AI client API
- Type safety is preserved through the use of dataclasses
- Session-based authentication requires OAuth flow to be completed in browser
