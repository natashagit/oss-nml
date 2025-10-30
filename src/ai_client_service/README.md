# AI Client Service

FastAPI service for AI client operations with OAuth 2.0 authentication via Google.

## Overview

This service provides:
- **OAuth 2.0 Authentication**: Google OAuth flow for user authentication
- **Chat Completions**: Generate chat completions using OpenAI's API
- **Streaming Support**: Real-time streaming of chat completions
- **User Management**: Per-user credential storage and management

## Features

- RESTful API endpoints for AI operations
- OAuth 2.0 authentication with Google
- Support for multiple AI models (GPT-3.5, GPT-4, etc.)
- Streaming chat completions
- Health check endpoint
- Comprehensive error handling

## API Endpoints

### Authentication
- `GET /oauth/authorize` - Initiate OAuth flow
- `POST /oauth/callback` - Handle OAuth callback

### AI Operations
- `POST /chat/completions` - Create chat completion
- `POST /chat/completions/stream` - Create streaming chat completion

### System
- `GET /health` - Health check

## Setup

### Environment Variables

```bash
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
OAUTH_REDIRECT_URI=http://localhost:8000/oauth/callback

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/ai_service

# Encryption Key (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
ENCRYPTION_KEY=your_base64_encoded_fernet_key
```

### Installation

```bash
# Install dependencies
pip install -e src/ai_client_api
pip install -e src/openai_client_impl
pip install -e src/ai_client_service
```

### Running the Service

```bash
# Start the service
python scripts/start_ai_service.py

# Or use uvicorn directly
uvicorn ai_client_service.main:app --host 0.0.0.0 --port 8000 --reload
```

The service will be available at:
- API: http://127.0.0.1:8000
- Documentation: http://127.0.0.1:8000/docs
- OpenAPI Spec: http://127.0.0.1:8000/openapi.json

## Usage

### Authentication Flow

1. Redirect user to `/oauth/authorize`
2. User completes Google OAuth flow
3. Google redirects to `/oauth/callback` with authorization code
4. Service exchanges code for tokens and stores user credentials

### Chat Completion

```python
import requests

# Create a chat completion
response = requests.post(
    "http://127.0.0.1:8000/chat/completions?user_id=user123",
    json={
        "messages": [
            {"role": "user", "content": "Hello, how are you?"}
        ],
        "model": "gpt-3.5-turbo",
        "temperature": 0.7
    }
)

result = response.json()
print(result["message"]["content"])
```

### Streaming Chat Completion

```python
import requests

# Create a streaming chat completion
response = requests.post(
    "http://127.0.0.1:8000/chat/completions/stream?user_id=user123",
    json={
        "messages": [
            {"role": "user", "content": "Tell me a story"}
        ],
        "model": "gpt-3.5-turbo"
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        chunk = json.loads(line.decode('utf-8'))
        print(chunk["content"], end="", flush=True)
```

## Testing

```bash
# Run tests
pytest src/ai_client_service/tests/

# Run with coverage
pytest src/ai_client_service/tests/ --cov=ai_client_service
```

## Development

### Code Quality

```bash
# Run linting
ruff check src/ai_client_service/

# Run type checking
mypy src/ai_client_service/
```

### Generating Service Client

After the service is running, generate the client library:

```bash
python scripts/generate_ai_service_client.py
```

This will create the `ai_client_service_client` package that can be used by the adapter.
