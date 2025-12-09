# AI Adapter

The `ai_adapter` package provides an adapter implementation that wraps the auto-generated service client and implements the `ai_api.AIInterface`.

## Overview

This adapter enables seamless switching between local and remote AI implementations:

- **Adapter Pattern** - Wraps service client to match interface
- **Network Abstraction** - Hides HTTP/REST complexity
- **Unified Interface** - Same code works for local or remote
- **Service Integration** - Enables distributed architecture

## Architecture

```
Consumer Code
    ↓
ai_api.get_client()
    ↓
ai_adapter.ServiceClient (Adapter)
    ↓
ai_service_client (Auto-generated HTTP client)
    ↓
HTTP Request → ai_service (FastAPI)
    ↓
openai_impl.OpenAIClient
    ↓
OpenAI API
```

## Usage

### Basic Setup

```python
import ai_adapter
from ai_api import get_client

# Register the adapter to point at the running service
ai_adapter.register(base_url="http://127.0.0.1:8000")

# Get the client (returns ServiceClient instance)
client = get_client()

# Use it exactly like the local implementation
response = client.generate_response(
    user_input="What is 2+2?",
    system_prompt="You are a math tutor."
)
print(response)  # "2+2 equals 4."
```

### Structured Output via Remote Service

```python
import ai_adapter
from ai_api import get_client

ai_adapter.register(base_url="http://127.0.0.1:8000")
client = get_client()

# Define a schema for structured output
schema = {
    "name": "email_action",
    "description": "Extract email action intent",
    "schema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["delete", "mark_as_read", "reply"]
            },
            "message_id": {"type": "string"}
        },
        "required": ["action"],
        "additionalProperties": False
    }
}

# Get structured response from remote service
result = client.generate_response(
    user_input="Delete email 12345",
    system_prompt="Extract the email action.",
    response_schema=schema
)
print(result)  # {"action": "delete", "message_id": "12345"}
```

### Switching Between Local and Remote

The power of this architecture is seamless switching:

```python
from ai_api import get_client

# Option 1: Local OpenAI implementation
import openai_impl  # Auto-registers
client = get_client()
response = client.generate_response("Hello", "Be friendly")

# Option 2: Remote AI service
import ai_adapter
ai_adapter.register(base_url="http://127.0.0.1:8000")
client = get_client()
response = client.generate_response("Hello", "Be friendly")

# Same interface, different implementation!
```

## ServiceClient

The adapter class that implements `ai_api.AIInterface`.

### Constructor

```python
ServiceClient(base_url: str = "http://127.0.0.1:8000")
```

**Parameters:**
- `base_url` - URL of the running AI service

### Methods

```python
def generate_response(
    user_input: str,
    system_prompt: str,
    response_schema: dict[str, Any] | None = None,
) -> str | dict[str, Any]:
    """Call the service /generate endpoint and return the result.
    
    Args:
        user_input: The text provided by the user
        system_prompt: Instructional system prompt
        response_schema: Optional JSON schema for structured output
        
    Returns:
        str: Conversational response (when response_schema is None)
        dict: Structured data (when response_schema is provided)
        
    Raises:
        RuntimeError: If the service returns no response
        TypeError: If the service returns a validation error
    """
```

## Factory Function

```python
def register(base_url: str = "http://127.0.0.1:8000") -> None:
    """Register the service adapter as the default AI client.
    
    Args:
        base_url: URL of the running AI service
    """
```

## How It Works

1. **Consumer calls** `ai_api.get_client()` → returns `ServiceClient` instance
2. **ServiceClient** wraps the auto-generated `ai_service_client.Client`
3. **HTTP request** is made to the FastAPI service at `/generate`
4. **Service** processes the request using `openai_impl`
5. **Response** is returned through the adapter to the consumer

The adapter handles:
- Converting method calls to HTTP requests
- Serializing/deserializing request/response data
- Error handling and validation
- Type conversions between generated client and interface

## Error Handling

The adapter provides clear error messages:

```python
import ai_adapter
from ai_api import get_client

ai_adapter.register(base_url="http://127.0.0.1:8000")
client = get_client()

try:
    response = client.generate_response("Hello", "Be helpful")
except RuntimeError as e:
    print(f"Service error: {e}")
except TypeError as e:
    print(f"Validation error: {e}")
```

## Configuration

### Custom Service URL

```python
import ai_adapter

# Development
ai_adapter.register(base_url="http://127.0.0.1:8000")

# Production
ai_adapter.register(base_url="https://ai-service.example.com")

# Docker
ai_adapter.register(base_url="http://ai-service:8000")
```

### Environment Variables

The adapter itself doesn't require environment variables, but the service it connects to needs:

```bash
export OPENAI_API_KEY="your_api_key_here"
```

## Testing

```bash
# Run unit tests
uv run pytest src/ai_adapter/tests/ -v

# Run with coverage
uv run pytest src/ai_adapter/tests/ --cov=src/ai_adapter --cov-report=term-missing
```

## Integration

- **ai_api** - Implements the `AIInterface` contract
- **ai_service** - The FastAPI service this adapter connects to
- **ai_service_client** - Auto-generated HTTP client (wrapped by this adapter)
- **openai_impl** - The actual AI implementation used by the service

## Design Patterns

1. **Adapter Pattern** - Wraps incompatible interface to match expected interface
2. **Dependency Injection** - Registers itself as the implementation via `register()`
3. **Proxy Pattern** - Acts as a proxy for remote service calls
4. **Separation of Concerns** - Network details hidden from business logic

## Benefits

- **Distributed Architecture** - AI processing can run on separate infrastructure
- **Scalability** - Service can be scaled independently
- **Flexibility** - Switch between local and remote without code changes
- **Testing** - Easy to mock or swap implementations
- **Deployment** - Service can be deployed to cloud platforms

## See Also

- [AI API Reference](ai_api.md) - Abstract interface
- [AI Service](ai_service.md) - The service this adapter connects to
- [AI Service Client](ai_service_client.md) - Auto-generated HTTP client
- [OpenAI Implementation](openai_impl.md) - Local implementation alternative
