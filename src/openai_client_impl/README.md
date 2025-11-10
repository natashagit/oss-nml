# OpenAI Client Implementation

Concrete implementation of the `ai_client_api` using OpenAI's API with OAuth 2.0 authentication via Google.

## Overview

This package provides:
- **OpenAIClient**: Implementation of the AI client that uses OpenAI's chat completion API
- **OAuthManager**: Handles Google OAuth 2.0 authentication flow

## Architecture

1. **User Authentication**: Users authenticate via Google OAuth 2.0 (handled by the service layer)
2. **API Key Resolution**: OpenAI API keys are resolved in priority order:
   - Explicit `openai_api_key` parameter
   - `OPENAI_API_KEY` environment variable
3. **API Access**: Each user's OpenAI API key is used to make API calls to OpenAI

## Setup

### Environment Variables

```bash
# Google OAuth Configuration (for OAuthManager)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
OAUTH_REDIRECT_URI=http://localhost:8000/oauth/callback

# OpenAI API Configuration
OPENAI_API_KEY=sk-proj-...  # Used if not provided per-user
```

### Installation

```bash
pip install -e src/ai_client_api
pip install -e src/openai_client_impl
```

## Usage

### Basic Usage (Local Implementation)

```python
from openai_client_impl import OpenAIClient
from ai_client_api.models import ChatMessage

# Create client for a specific user
# Will use OPENAI_API_KEY from environment if not provided
client = OpenAIClient(user_id="user123", openai_api_key="sk-proj-...")

# Generate a chat completion
messages = [
    ChatMessage(role="user", content="What is the capital of France?")
]
response = client.chat_completion(messages, model="gpt-3.5-turbo")
print(response.message.content)

# Stream a chat completion
for chunk in client.chat_completion_stream(messages, model="gpt-3.5-turbo"):
    if chunk.content:
        print(chunk.content, end="", flush=True)
```

### Registering with the API

```python
import ai_client_api
from openai_client_impl import register

# Register this implementation globally
# This makes get_client() return OpenAIClient instances
register()

# Now you can use the abstract API
client = ai_client_api.get_client(user_id="user123")
messages = [
    ai_client_api.models.ChatMessage(role="user", content="Hello!")
]
response = client.chat_completion(messages)
```

### OAuth Flow (Service Layer)

OAuth authentication is typically handled by the `ai_client_service` layer. The `OAuthManager` can be used directly if needed:

```python
from openai_client_impl import OAuthManager

oauth_manager = OAuthManager(credential_store=None)  # No database needed

# Step 1: Get authorization URL
auth_url, state = oauth_manager.get_authorization_url(state="random_state")
print(f"Visit this URL to authorize: {auth_url}")

# Step 2: After user authorizes, handle the callback
user_info = oauth_manager.handle_callback(
    authorization_response=callback_url,
    state=state
)
print(f"Authenticated user: {user_info['user_id']}")
```

## API Key Resolution Priority

The `OpenAIClient` resolves API keys in the following order:

1. **Explicit parameter**: `openai_api_key` passed to constructor
2. **Environment variable**: `OPENAI_API_KEY`

## Security Notes

- API keys are never logged or exposed in error messages
- Use HTTPS in production for OAuth redirect URIs
- API keys should be kept secure and not committed to version control

## Dependencies

- `openai`: OpenAI Python SDK
- `google-auth`: Google authentication library
- `google-auth-oauthlib`: OAuth 2.0 flow handler
