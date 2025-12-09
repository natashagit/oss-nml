# AI API

The `ai_api` package defines the abstract interface (contract) for all AI implementations in the system.

## Overview

This package provides the foundation for the AI service architecture through:

- **AIInterface (ABC)** - Abstract base class defining the contract
- **get_client()** - Factory function returning the registered implementation
- **Dependency Injection** - Implementations register themselves at runtime

## AIInterface

::: ai_api.AIInterface
    options:
      show_source: false
      members:
        - generate_response

## Factory Function

```python
def get_client() -> AIInterface:
    """Return an instance of the registered AI client implementation."""
```

The `get_client()` function is designed to be "patched" by implementations during their import/registration.

## Usage

### Basic Usage

```python
import openai_impl  # Registers the OpenAI implementation
from ai_api import get_client

# Get the registered client
client = get_client()

# Generate a response
response = client.generate_response(
    user_input="What is the capital of France?",
    system_prompt="You are a helpful geography assistant."
)
print(response)  # "The capital of France is Paris."
```

### Structured Output

```python
from ai_api import get_client

client = get_client()

# Define a schema for structured output
schema = {
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

# Get structured response
result = client.generate_response(
    user_input="Create a ticket to fix login redirect.",
    system_prompt="Extract intent and title fields.",
    response_schema=schema,
)
print(result)  # {"intent": "create_ticket", "title": "Fix login redirect"}
```

### Switching Implementations

The power of this architecture is seamless implementation switching:

```python
# Option 1: Use local OpenAI implementation
import openai_impl  # Auto-registers on import
from ai_api import get_client

client = get_client()  # Returns OpenAIClient

# Option 2: Use remote AI service
import ai_adapter
ai_adapter.register(base_url="http://localhost:8000")
from ai_api import get_client

client = get_client()  # Returns ServiceClient (calls remote API)

# Consumer code remains identical!
response = client.generate_response("Hello", "You are helpful.")
```

## Dependency Injection Pattern

Implementations register themselves by patching the `get_client()` function:

```python
import ai_api
from ai_api import AIInterface

# Initially, get_client() raises NotImplementedError
try:
    client = ai_api.get_client()
except NotImplementedError:
    print("No implementation registered yet")

# Implementations register by patching get_client()
def register_my_impl():
    def _get_client() -> AIInterface:
        return MyCustomAIClient()
    
    ai_api.get_client = _get_client

# Now get_client() returns your implementation
register_my_impl()
client = ai_api.get_client()  # Returns MyCustomAIClient instance
```

## Response Schema Format

When using structured output, the `response_schema` should follow this format:

```python
{
    "name": "schema_name",           # Name of the schema
    "description": "What it does",   # Description of the schema
    "schema": {                      # JSON Schema specification
        "type": "object",
        "properties": {
            "field1": {"type": "string"},
            "field2": {"type": "integer"}
        },
        "required": ["field1"],
        "additionalProperties": False
    }
}
```

## Method Reference

### generate_response

```python
def generate_response(
    user_input: str,
    system_prompt: str,
    response_schema: dict[str, Any] | None = None,
) -> str | dict[str, Any]:
    """Generate a response from the AI.
    
    Args:
        user_input: The text provided by the chat user
        system_prompt: The instruction set (e.g., "You are a helpful assistant...")
        response_schema: Optional JSON schema dict for structured output
        
    Returns:
        str: Conversational response (when response_schema is None)
        dict: Structured data matching schema (when response_schema is provided)
    """
```

## Design Principles

1. **Single Responsibility** - Defines only the contract, no implementation
2. **Open/Closed** - Open for extension (new implementations), closed for modification
3. **Dependency Inversion** - High-level code depends on abstractions
4. **Interface Segregation** - Minimal, focused interface

## Integration

- **openai_impl** - Provides concrete implementation using OpenAI API
- **ai_service** - FastAPI service exposing the interface via REST
- **ai_adapter** - Adapter wrapping service client to match this interface
- **ai_service_client** - Auto-generated client for calling the service

## Testing

```bash
# Run unit tests
uv run pytest src/ai_api/tests/ -v

# Run with coverage
uv run pytest src/ai_api/tests/ --cov=src/ai_api --cov-report=term-missing
```

## See Also

- [OpenAI Implementation](openai_impl.md) - Concrete implementation
- [AI Service](ai_service.md) - REST service wrapper
- [AI Adapter](ai_adapter.md) - Remote service adapter
