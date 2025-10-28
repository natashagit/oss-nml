# OpenAI Client Implementation

Concrete implementation of the `ai_client_api` using OpenAI's API with OAuth 2.0 authentication via Google.

## Overview

This package provides:
- **OpenAIClient**: Implementation of the AI client that uses OpenAI's chat completion API
- **OAuthManager**: Handles Google OAuth 2.0 authentication flow
- **CredentialStore**: Securely stores user credentials in PostgreSQL with encryption

## Architecture

1. **User Authentication**: Users authenticate via Google OAuth 2.0
2. **Credential Storage**: Google refresh tokens and OpenAI API keys are encrypted and stored in PostgreSQL
3. **API Access**: Each user's OpenAI API key is retrieved from the database and used to make API calls

## Setup

### Environment Variables

```bash
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
OAUTH_REDIRECT_URI=http://localhost:8000/oauth/callback

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/openai_service

# Encryption Key (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
ENCRYPTION_KEY=your_base64_encoded_fernet_key
```

### Database Setup

```bash
# Create PostgreSQL database
createdb openai_service

# The schema will be created automatically on first run
```

## Usage

### Basic Usage

```python
from openai_client_impl import OpenAIClient, CredentialStore

# Initialize credential store
credential_store = CredentialStore()

# Create client for a specific user
client = OpenAIClient(user_id="google_user_123", credential_store=credential_store)

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

### OAuth Flow

```python
from openai_client_impl import OAuthManager, CredentialStore

credential_store = CredentialStore()
oauth_manager = OAuthManager(credential_store)

# Step 1: Get authorization URL
auth_url, state = oauth_manager.get_authorization_url()
print(f"Visit this URL to authorize: {auth_url}")

# Step 2: After user authorizes, handle the callback
# (callback_url is the full URL that Google redirects to)
user_info = oauth_manager.handle_callback(
    authorization_response=callback_url,
    state=state
)

# Step 3: Store the user's OpenAI API key
credential_store.store_user_credentials(
    user_id=user_info["user_id"],
    email=user_info["email"],
    openai_api_key="sk-..."
)
```

### Registering with the API

```python
import ai_client_api
from openai_client_impl import register, CredentialStore

# Register this implementation
credential_store = CredentialStore()
register(credential_store)

# Now you can use the abstract API
client = ai_client_api.get_client(user_id="google_user_123")
```

## Security Notes

- All credentials are encrypted at rest using Fernet symmetric encryption
- The `ENCRYPTION_KEY` should be kept secret and backed up securely
- Use HTTPS in production for the OAuth redirect URI
- Consider using environment-specific encryption keys for dev/staging/prod

## Dependencies

- `openai`: OpenAI Python SDK
- `psycopg2-binary`: PostgreSQL adapter
- `sqlalchemy`: ORM for database operations
- `google-auth`: Google authentication library
- `google-auth-oauthlib`: OAuth 2.0 flow handler
- `cryptography`: Encryption for credentials
