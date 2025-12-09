# AI Service Client

The `ai_service_client` package is an auto-generated Python client library for accessing the AI Service REST API.

## Overview

This client is generated from the OpenAPI specification using `openapi-python-client`:

- **Auto-Generated** - Created from OpenAPI spec, ensuring API compatibility
- **Type-Safe** - Full type hints for IDE support and type checking
- **HTTP Client** - Handles HTTP requests, serialization, and deserialization
- **Wrapped by Adapter** - Used internally by `ai_adapter` to implement `ai_api.AIInterface`

## Usage

### Basic Usage

```python
from ai_service_client import Client
from ai_service_client.api.default import generate_generate_post
from ai_service_client.models import GenerateRequest

# Create a client
client = Client(base_url="http://127.0.0.1:8000")

# Create a request
request = GenerateRequest(
    user_input="What is 2+2?",
    system_prompt="You are a math tutor.",
    response_schema=None
)

# Make the API call
response = generate_generate_post.sync(client=client, body=request)

print(response.result)  # "2+2 equals 4."
```

### Structured Output

```python
from ai_service_client import Client
from ai_service_client.api.default import generate_generate_post
from ai_service_client.models import GenerateRequest

client = Client(base_url="http://127.0.0.1:8000")

schema = {
    "name": "ticket_command",
    "description": "Extract intent and title",
    "schema": {
        "type": "object",
        "properties": {
            "intent": {"type": "string"},
            "title": {"type": "string"}
        },
        "required": ["intent", "title"],
        "additionalProperties": False
    }
}

request = GenerateRequest(
    user_input="Create a ticket to fix login redirect",
    system_prompt="Extract intent and title",
    response_schema=schema
)

response = generate_generate_post.sync(client=client, body=request)
print(response.result)  # {"intent": "create_ticket", "title": "Fix login redirect"}
```

## Typical Usage Pattern

Most users won't use this client directly. Instead, use the `ai_adapter`:

```python
# Instead of direct client usage:
from ai_service_client import Client
from ai_service_client.api.default import generate_generate_post
from ai_service_client.models import GenerateRequest

client = Client(base_url="http://127.0.0.1:8000")
request = GenerateRequest(user_input="Hello", system_prompt="Be helpful")
response = generate_generate_post.sync(client=client, body=request)

# Use this (via adapter):
import ai_adapter
from ai_api import get_client

ai_adapter.register(base_url="http://127.0.0.1:8000")
client = get_client()
response = client.generate_response("Hello", "Be helpful")
```

The adapter provides a cleaner, more Pythonic interface that matches the local implementation.

## Client Configuration

### Basic Client

```python
from ai_service_client import Client

client = Client(base_url="http://127.0.0.1:8000")
```

### Authenticated Client

```python
from ai_service_client import AuthenticatedClient

client = AuthenticatedClient(
    base_url="http://127.0.0.1:8000",
    token="SuperSecretToken"
)
```

### Custom SSL Certificate

```python
from ai_service_client import Client

client = Client(
    base_url="https://internal-api.example.com",
    verify_ssl="/path/to/certificate_bundle.pem"
)
```

## Regenerating the Client

This client is auto-generated from the OpenAPI spec. To regenerate:

```bash
# Start the AI service
uv run uvicorn ai_service.main:app --reload

# Generate the client (in another terminal)
openapi-python-client generate --url http://127.0.0.1:8000/openapi.json \
  --output-path src/ai_service_client

# Or from a saved spec file
openapi-python-client generate --path openapi.json \
  --output-path src/ai_service_client
```

## API Methods

### generate_generate_post

Call the `/generate` endpoint to generate AI responses.

**Sync Methods:**
- `sync(client, body)` - Returns parsed data or None
- `sync_detailed(client, body)` - Returns full Response object

**Async Methods:**
- `asyncio(client, body)` - Async version of sync
- `asyncio_detailed(client, body)` - Async version of sync_detailed

## Models

### GenerateRequest

```python
from ai_service_client.models import GenerateRequest

request = GenerateRequest(
    user_input="Your question here",
    system_prompt="System instructions",
    response_schema=None  # Optional: dict for structured output
)
```

### GenerateResponse

```python
# Response object
response.result  # str | dict - The AI-generated result
```

## Integration

- **ai_service** - The FastAPI service this client connects to
- **ai_adapter** - Wraps this client to implement `ai_api.AIInterface`
- **ai_api** - The interface that the adapter implements

## Type Checking

The generated client includes full type hints:

```python
from ai_service_client import Client
from ai_service_client.models import GenerateRequest, GenerateResponse
from ai_service_client.types import Response

# All types are properly annotated
client: Client = Client(base_url="http://127.0.0.1:8000")
request: GenerateRequest = GenerateRequest(...)
response: GenerateResponse | None = generate_generate_post.sync(...)
detailed: Response[GenerateResponse] = generate_generate_post.sync_detailed(...)
```

## Testing

This is an auto-generated client, so it's tested indirectly through:
- `ai_adapter` tests
- `ai_service` integration tests
- End-to-end tests

## See Also

- [AI Service](ai_service.md) - The service this client connects to
- [AI Adapter](ai_adapter.md) - Wrapper that implements the interface
- [AI API Reference](ai_api.md) - The interface specification
