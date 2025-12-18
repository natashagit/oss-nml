# AI Ticket Service

The AI Ticket Service is a FastAPI application that uses natural language processing to create and manage tickets across different backends (Google Tasks, Trello).

## Quick Start

### 1. Environment Setup

Copy the example environment file and configure it:

```bash
cp .env.example .env
# Edit .env with your actual credentials
```

### 2. Running the Service

#### Option A: Local Development (Recommended)
```bash
# Install dependencies and run with hot reload
uv run --extra dev uvicorn ai_ticket_service.main:app --reload --port 8000
```

#### Option B: Using Docker (Root Dockerfile)
```bash
# Build the image
docker build -t ai-ticket-service .

# Run with environment file
docker run -p 8000:8000 --env-file .env ai-ticket-service
```

#### Option C: Using Docker Compose (Full Stack)
```bash
cd deploy
docker-compose up --build
```

### 3. Access the Service

- **Main API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Environment Variables

### Required
- `OPENAI_API_KEY`: Your OpenAI API key for AI processing

### Backend Configuration

#### Google Tasks Backend
- `TASKS_CLIENT_ID`: Google OAuth client ID
- `TASKS_CLIENT_SECRET`: Google OAuth client secret  
- `TASKS_REFRESH_TOKEN`: Google OAuth refresh token
- `TASKS_INTERACTIVE`: Set to `false` for non-interactive mode

#### Trello Backend
- `TRELLO_API_KEY`: Trello API key
- `TRELLO_API_SECRET`: Trello API secret
- `TRELLO_TOKEN`: Trello access token
- `TRELLO_BOARD_ID`: Target Trello board ID
- `REDIRECT_URI`: OAuth redirect URI (default: http://localhost:8000/callback)

#### Discord Integration (Optional)
- `DISCORD_BOT_TOKEN`: Discord bot token
- `DISCORD_DEFAULT_TOKEN_TYPE`: Token type (default: Bot)
- `CHAT_CHANNEL_ID`: Discord channel ID for notifications

## API Usage Examples

### Create a Ticket (Trello)
```bash
curl -X POST http://localhost:8000/command \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "create a ticket for fixing the login bug",
    "system_prompt": "You are a helpful assistant that creates tickets",
    "backend": "trello"
  }'
```

### Create a Ticket (Google Tasks)
```bash
curl -X POST http://localhost:8000/command \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "create a task for database optimization",
    "system_prompt": "You are a helpful assistant that creates tickets",
    "backend": "google_tasks"
  }'
```

### Update a Ticket
```bash
curl -X POST http://localhost:8000/command \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "update ticket abc123 to completed status",
    "system_prompt": "You are a helpful assistant that updates tickets",
    "backend": "trello"
  }'
```

## Development

### Running Tests
```bash
# Run all tests
uv run python -m pytest src/ tests/ -v

# Run with coverage
uv run python -m pytest src/ tests/ --cov=src --cov-report=term-missing
```

### Code Quality
```bash
# Linting
uv run ruff check .

# Type checking
uv run mypy src/ai_ticket_service/

# Format code
uv run ruff format .
```

## Architecture

The service consists of several components:

- **AI API**: Natural language processing interface
- **Ticket Backends**: Google Tasks and Trello integrations
- **FastAPI Service**: REST API for ticket operations
- **Adapters**: Client libraries for easy integration

## Monitoring

When using Docker Compose, the service includes:

- **Prometheus**: Metrics collection (http://localhost:9090)
- **Grafana**: Metrics visualization (http://localhost:3000)

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed with `uv sync --extra dev`
2. **Authentication Errors**: Verify your API keys and tokens in `.env`
3. **Port Conflicts**: Change the port if 8000 is already in use: `--port 8001`

### Logs

Check application logs for detailed error information:
```bash
# Docker logs
docker logs <container-id>

# Docker Compose logs
docker-compose logs ai_service
```

## Contributing

1. Install development dependencies: `uv sync --extra dev`
2. Run tests: `uv run python -m pytest`
3. Check code quality: `uv run ruff check .`
4. Submit pull request

For more detailed deployment information, see `deploy/README.md`.