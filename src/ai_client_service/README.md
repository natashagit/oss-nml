# AI Client Service

FastAPI service for AI client operations with OAuth 2.0 authentication via Google and session-based credential storage.

## Overview

This service provides:
- **OAuth 2.0 Authentication**: Google OAuth flow for user authentication
- **Session Management**: Stores user authentication state and API keys in encrypted sessions
- **Chat Completions**: Generate chat completions using OpenAI's API
- **Streaming Support**: Real-time streaming of chat completions

## Features

- RESTful API endpoints for AI operations
- OAuth 2.0 authentication with Google
- Session-based credential storage (no database required)
- Support for multiple AI models (GPT-3.5, GPT-4, etc.)
- Streaming chat completions
- Health check endpoint
- Comprehensive error handling
- Interactive API documentation (Swagger UI)

## API Endpoints

### Authentication
- `GET /oauth/authorize` - Initiate OAuth flow (redirects to Google)
- `GET /oauth/callback` - Handle OAuth callback from Google

### User Management
- `POST /api-keys` - Set OpenAI API key for authenticated user (stored in session)

### AI Operations
- `POST /chat/completions` - Create chat completion
- `POST /chat/completions/stream` - Create streaming chat completion

### System
- `GET /health` - Health check endpoint

## Setup

### Environment Variables

```bash
# Google OAuth Configuration (REQUIRED)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
OAUTH_REDIRECT_URI=http://localhost:8000/oauth/callback

# OpenAI API Configuration (REQUIRED)
OPENAI_API_KEY=sk-proj-...

# Session Configuration (Optional)
SESSION_SECRET_KEY=your-secret-key  # Auto-generated if not set
SESSION_MAX_AGE=86400  # Session expiration in seconds (default: 24 hours)
HTTPS_ONLY=false  # Set to true for production
```

### Installation

```bash
# Install dependencies
uv sync --all-packages --extra dev

# Or manually
pip install -e src/ai_client_api
pip install -e src/openai_client_impl
pip install -e src/ai_client_service
```

### Running the Service

#### Using uvicorn directly:

```bash
# Set environment variables
export GOOGLE_CLIENT_ID="your-client-id"
export GOOGLE_CLIENT_SECRET="your-client-secret"
export OAUTH_REDIRECT_URI="http://127.0.0.1:8000/oauth/callback"
export OPENAI_API_KEY="sk-proj-..."

# Start the service
uv run uvicorn ai_client_service.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Using Docker:

```bash
# Create .env file
cp .env.example .env
# Edit .env with your credentials

# Build and run
docker-compose up --build -d
```

The service will be available at:
- API: http://127.0.0.1:8000
- Documentation: http://127.0.0.1:8000/docs
- Health Check: http://127.0.0.1:8000/health
- OpenAPI Spec: http://127.0.0.1:8000/openapi.json

## Usage

### Complete Authentication Flow

1. **Initiate OAuth**: Visit `http://localhost:8000/oauth/authorize` or use Swagger UI
2. **Google Sign-In**: You'll be redirected to Google to sign in
3. **Callback**: Google redirects back to `/oauth/callback` with your user info
4. **Set API Key**: Use `POST /api-keys` to store your OpenAI API key in the session
5. **Use AI Service**: Make requests to `POST /chat/completions` or `/chat/completions/stream`

### Using Swagger UI

1. Start the service
2. Open http://127.0.0.1:8000/docs
3. Click on `GET /oauth/authorize` → "Try it out" → "Execute"
4. Copy the authorization URL and open it in your browser
5. Complete Google sign-in
6. After redirect, use `POST /api-keys` to set your OpenAI API key
7. Use `POST /chat/completions` to chat with AI

### Chat Completion (Python)

```python
import requests

# Step 1: Complete OAuth (in browser)
# Visit: http://localhost:8000/oauth/authorize

# Step 2: Set API key (using session cookie from OAuth)
response = requests.post(
    "http://127.0.0.1:8000/api-keys",
    json={"openai_api_key": "sk-proj-..."},
    cookies={"session": "your-session-cookie"}  # From OAuth flow
)

# Step 3: Create a chat completion
response = requests.post(
    "http://127.0.0.1:8000/chat/completions",
    json={
        "messages": [
            {"role": "user", "content": "Hello, how are you?"}
        ],
        "model": "gpt-3.5-turbo",
        "temperature": 0.7
    },
    cookies={"session": "your-session-cookie"}
)

result = response.json()
print(result["message"]["content"])
```

### Streaming Chat Completion

```python
import requests
import json

response = requests.post(
    "http://127.0.0.1:8000/chat/completions/stream",
    json={
        "messages": [
            {"role": "user", "content": "Tell me a story"}
        ],
        "model": "gpt-3.5-turbo"
    },
    cookies={"session": "your-session-cookie"},
    stream=True
)

for line in response.iter_lines():
    if line:
        chunk = json.loads(line.decode('utf-8'))
        if chunk.get("content"):
            print(chunk["content"], end="", flush=True)
```

## Architecture

The service uses:
- **Session-based storage**: User authentication and API keys stored in encrypted sessions (no database)
- **OAuth 2.0**: Google OAuth for user authentication
- **Dependency Injection**: FastAPI dependencies for authentication and client creation
- **Type-safe models**: Pydantic models for request/response validation

## Testing

```bash
# Run tests
uv run pytest src/ai_client_service/tests/

# Run with coverage
uv run pytest src/ai_client_service/tests/ --cov=ai_client_service
```

## Development

### Code Quality

```bash
# Run linting
uv run ruff check src/ai_client_service/

# Run type checking
uv run mypy src/ai_client_service/
```

### Generating Service Client

After the service is running, generate the client library:

```bash
# Start the service first
uv run uvicorn ai_client_service.main:app --host 127.0.0.1 --port 8000

# In another terminal, generate the client
uv run openapi-python-client generate \
    --url http://127.0.0.1:8000/openapi.json \
    --output src/ai_client_service_client
```

This will create the `ai_client_service_client` package that can be used by the adapter.
