# AI Service

The `ai_service` package is a FastAPI web service that exposes the `ai_api.AIInterface` via REST endpoints.

## Overview

This service enables distributed AI processing by:

- **REST API** - HTTP endpoints for AI functionality
- **OpenAPI Spec** - Auto-generated documentation and client code
- **Scalability** - Can be deployed and scaled independently
- **Cloud Ready** - Containerized and deployable to cloud platforms

## API Endpoints

### Health Check

**GET** `/health`

Check if the service is running.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

**Example:**
```bash
curl http://127.0.0.1:8000/health
```

### Generate Response

**POST** `/generate`

Generate an AI response (conversational or structured).

**Request Body:**
```json
{
  "user_input": "What is the capital of France?",
  "system_prompt": "You are a helpful geography assistant.",
  "response_schema": null
}
```

**Response:**
```json
{
  "result": "The capital of France is Paris."
}
```

## Running the Service

### Development Mode

```bash
# Start with auto-reload
uv run uvicorn ai_service.main:app --reload

# Custom host/port
uv run uvicorn ai_service.main:app --host 0.0.0.0 --port 8080 --reload
```

The service will be available at `http://127.0.0.1:8000`.

### Production Mode

```bash
# Run with multiple workers
uv run uvicorn ai_service.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Docker

```bash
# Build the image
docker build -t ai-service .

# Run the container
docker run -p 8000:8000 -e OPENAI_API_KEY="your_key" ai-service
```

## Usage Examples

### Conversational Request

```bash
curl -X POST http://127.0.0.1:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Say hello in 3 words",
    "system_prompt": "You are concise."
  }'
```

**Response:**
```json
{
  "result": "Hello there friend!"
}
```

### Structured Output Request

```bash
curl -X POST http://127.0.0.1:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Create a ticket to fix login redirect",
    "system_prompt": "Extract intent and title",
    "response_schema": {
      "name": "ticket_command",
      "description": "Extract intent and title",
      "schema": {
        "type": "object",
        "properties": {
          "intent": {"type": "string"},
          "title": {"type": "string"}
        },
        "required": ["intent", "title"],
        "additionalProperties": false
      }
    }
  }'
```

**Response:**
```json
{
  "result": {
    "intent": "create_ticket",
    "title": "Fix login redirect"
  }
}
```

### Python Client (using ai_adapter)

```python
import ai_adapter
from ai_api import get_client

# Register the adapter to use the service
ai_adapter.register(base_url="http://127.0.0.1:8000")

# Get client and use it
client = get_client()
response = client.generate_response(
    user_input="What is 2+2?",
    system_prompt="You are a math tutor."
)
print(response)  # "2+2 equals 4."
```

### Direct HTTP Requests

```python
import requests

response = requests.post(
    "http://127.0.0.1:8000/generate",
    json={
        "user_input": "Hello!",
        "system_prompt": "You are friendly.",
        "response_schema": None
    }
)
print(response.json())  # {"result": "Hello! How can I help you today?"}
```

## Configuration

### Environment Variables

```bash
# Required
export OPENAI_API_KEY="your_openai_api_key"

# Optional
export HOST="127.0.0.1"  # Default: 127.0.0.1
export PORT="8000"        # Default: 8000
```

### .env File

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
HOST=127.0.0.1
PORT=8000
```

## API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **OpenAPI JSON**: http://127.0.0.1:8000/openapi.json

## Request/Response Models

### GenerateRequest

```python
{
    "user_input": str,           # Required: User's input text
    "system_prompt": str,        # Required: System instruction
    "response_schema": dict | None  # Optional: JSON schema for structured output
}
```

### GenerateResponse

```python
{
    "result": str | dict  # Conversational string or structured dict
}
```

### HealthCheckResponse

```python
{
    "status": str,    # "healthy"
    "version": str    # Service version
}
```

## Error Handling

The service returns appropriate HTTP status codes:

- **200 OK** - Successful response
- **422 Unprocessable Entity** - Invalid request body
- **500 Internal Server Error** - AI client failure or generation error

**Example Error Response:**
```json
{
  "detail": "Failed to generate response: API key invalid"
}
```

## Deployment

### Docker

```bash
# Build
docker build -t ai-service .

# Run
docker run -p 8000:8000 \
  -e OPENAI_API_KEY="your_key" \
  ai-service
```

### Fly.io

```bash
# Deploy
fly deploy

# Set secrets
fly secrets set OPENAI_API_KEY="your_key"

# Check status
fly status
```

### Cloud Platforms

The service can be deployed to:
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances
- Heroku
- Railway

## Performance

- **Async Support** - FastAPI is async-capable for high concurrency
- **Workers** - Use multiple workers for production (`--workers 4`)
- **Caching** - Consider adding response caching for repeated queries
- **Rate Limiting** - Add rate limiting middleware for production
- **Monitoring** - Integrate with monitoring tools (Prometheus, DataDog)

## Security

- **API Keys** - Never commit API keys to version control
- **Environment Variables** - Use environment variables or secrets management
- **HTTPS** - Use HTTPS in production (handled by deployment platform)
- **Authentication** - Consider adding API authentication for production
- **CORS** - Configure CORS if accessed from web browsers

## Testing

```bash
# Run unit tests
uv run pytest src/ai_service/tests/ -v

# Run with coverage
uv run pytest src/ai_service/tests/ --cov=src/ai_service --cov-report=term-missing

# Test the running service
curl http://127.0.0.1:8000/health
```

## Integration

- **ai_api** - Implements the interface defined here
- **openai_impl** - Default AI implementation used by the service
- **ai_adapter** - Client adapter that calls this service
- **ai_service_client** - Auto-generated HTTP client for this service

## Monitoring and Logging

The service uses Python's standard logging:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

## See Also

- [AI API Reference](ai_api.md) - Abstract interface
- [OpenAI Implementation](openai_impl.md) - Concrete implementation
- [AI Adapter](ai_adapter.md) - Client adapter
- [AI Service Client](ai_service_client.md) - Auto-generated client
