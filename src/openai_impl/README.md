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

### Structured Output
```python
import openai_impl

client = openai_impl.OpenAIClient()

schema = {
    "type": "object",
    "properties": {
        "temperature": {"type": "number"},
        "conditions": {"type": "string"}
    }
}

response = client.generate_response(
    user_input="What is the weather in NYC?",
    system_prompt="Extract weather information.",
    response_schema=schema
)
print(response)  # Returns a dict matching the schema
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
