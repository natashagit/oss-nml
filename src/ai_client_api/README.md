# AI Client API

Abstract API contract for AI client services. This package defines the interface that all AI client implementations must follow.

## Overview

This package provides the abstract base class `Client` that defines the contract for AI services, focusing on chat completion capabilities.

## Usage

```python
from ai_client_api import Client, get_client

# Get a client instance for a specific user
client = get_client(user_id="user123")

# Generate a chat completion
messages = [
    {"role": "user", "content": "Hello, how are you?"}
]
response = client.chat_completion(messages)

# Stream a chat completion
for chunk in client.chat_completion_stream(messages):
    print(chunk)
```
