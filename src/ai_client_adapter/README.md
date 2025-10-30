# AI Client Adapter

Service client adapter that implements the AI client API using the generated service client.

## Overview

This package provides:
- **ServiceClient**: Adapter that wraps the generated AI service client
- **Location Transparency**: Same interface whether using local or remote AI client
- **Network Abstraction**: Hides HTTP details from the consumer

## Architecture

The adapter implements the `ai_client_api.Client` interface by:
1. Converting API calls to HTTP requests to the AI service
2. Handling authentication and user context
3. Transforming responses back to the expected format
4. Providing streaming support for chat completions

## Setup

### Prerequisites

1. The AI service must be running and accessible
2. The service client must be generated using `openapi-python-client`

### Installation

```bash
# Install dependencies
pip install -e src/ai_client_api
pip install -e src/ai_client_service_client  # Generated client
pip install -e src/ai_client_adapter
```

### Generating the Service Client

First, start the AI service:

```bash
python scripts/start_ai_service.py
```

Then generate the service client:

```bash
python scripts/generate_ai_service_client.py
```

## Usage

### Basic Usage

```python
from ai_client_adapter import ServiceClient

# Create adapter pointing to the AI service
client = ServiceClient(
    base_url="http://127.0.0.1:8000",
    user_id="user123"
)

# Generate a chat completion
messages = [
    {"role": "user", "content": "What is the capital of France?"}
]
response = client.chat_completion(messages)
print(response["message"]["content"])

# Stream a chat completion
for chunk in client.chat_completion_stream(messages):
    print(chunk["content"], end="", flush=True)
```

### Integration with Existing Code

The adapter can be used as a drop-in replacement for the local AI client:

```python
from ai_client_api import get_client
from ai_client_adapter import ServiceClient

# Local usage (original)
local_client = get_client(user_id="user123")

# Remote usage (adapter)
remote_client = ServiceClient(
    base_url="https://your-ai-service.com",
    user_id="user123"
)

# Both clients have the same interface
response1 = local_client.chat_completion(messages)
response2 = remote_client.chat_completion(messages)
```

## API Reference

### ServiceClient

#### `__init__(base_url: str, user_id: str)`

Initialize the service client adapter.

**Parameters:**
- `base_url`: Base URL of the AI service
- `user_id`: User ID for authentication

#### `chat_completion(messages, model, temperature, max_tokens)`

Generate a chat completion.

**Parameters:**
- `messages`: List of message dicts with 'role' and 'content' keys
- `model`: AI model to use (default: "gpt-3.5-turbo")
- `temperature`: Sampling temperature (default: 0.7)
- `max_tokens`: Maximum tokens to generate (optional)

**Returns:**
- Dictionary containing the completion response

#### `chat_completion_stream(messages, model, temperature, max_tokens)`

Generate a streaming chat completion.

**Parameters:**
- `messages`: List of message dicts with 'role' and 'content' keys
- `model`: AI model to use (default: "gpt-3.5-turbo")
- `temperature`: Sampling temperature (default: 0.7)
- `max_tokens`: Maximum tokens to generate (optional)

**Yields:**
- Chunks of the completion response as they're generated

## Testing

```bash
# Run tests
pytest src/ai_client_adapter/tests/

# Run with coverage
pytest src/ai_client_adapter/tests/ --cov=ai_client_adapter
```

## Development

### Code Quality

```bash
# Run linting
ruff check src/ai_client_adapter/

# Run type checking
mypy src/ai_client_adapter/
```

## Notes

- The adapter requires the generated service client to be available
- All network requests are synchronous (async support can be added if needed)
- Error handling follows the same patterns as the local implementation
- The adapter maintains the same interface as the original AI client API
