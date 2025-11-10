# AI Client API

Abstract API contract for AI client services. This package defines the interface that all AI client implementations must follow.

## Overview

This package provides the abstract base class `Client` that defines the contract for AI services, focusing on chat completion capabilities. It uses type-safe dataclasses for messages and responses.

## Models

- **`ChatMessage`**: A single message in a chat conversation (role, content)
- **`ChatCompletionResponse`**: Response model for chat completion (message, model, usage, finish_reason)
- **`ChatCompletionChunk`**: A single chunk in a streaming chat completion
- **`TokenUsage`**: Token usage information (prompt_tokens, completion_tokens, total_tokens)

## Usage

```python
from ai_client_api import Client, get_client
from ai_client_api.models import ChatMessage

# Get a client instance for a specific user
client = get_client(user_id="user123")

# Generate a chat completion
messages = [
    ChatMessage(role="user", content="Hello, how are you?")
]
response = client.chat_completion(messages, model="gpt-3.5-turbo")
print(response.message.content)
print(f"Tokens used: {response.usage.total_tokens}")

# Stream a chat completion
for chunk in client.chat_completion_stream(messages, model="gpt-3.5-turbo"):
    if chunk.content:
        print(chunk.content, end="", flush=True)
```

## Interface

The `Client` abstract base class defines:

- `chat_completion(messages: list[ChatMessage], model: str, temperature: float, max_tokens: int | None) -> ChatCompletionResponse`
- `chat_completion_stream(messages: list[ChatMessage], model: str, temperature: float, max_tokens: int | None) -> Iterator[ChatCompletionChunk]`

## Implementation

To create a new implementation:

1. Inherit from `ai_client_api.Client`
2. Implement `chat_completion` and `chat_completion_stream` methods
3. Register your implementation using the registration mechanism
