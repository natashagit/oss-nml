# AI Ticket Service Deployment

This directory contains Docker configuration for deploying the AI Ticket Service with monitoring.

## Services

- **ai_service**: The main AI Ticket Service (port 8000)
- **prometheus**: Metrics collection (port 9090)
- **grafana**: Metrics visualization (port 3000)

## Quick Start

### 1. Set Environment Variables

Create a `.env` file in the deploy directory:

```bash
# Required
OPENAI_API_KEY=your-openai-api-key

# Optional - For Trello backend
TRELLO_API_KEY=your-trello-api-key
TRELLO_API_SECRET=your-trello-api-secret
TRELLO_TOKEN=your-trello-token
TRELLO_BOARD_ID=your-trello-board-id
REDIRECT_URI=http://localhost:8000/callback

# Optional - For Google Tasks backend
TASKS_INTERACTIVE=false

# Optional - For Discord integration
DISCORD_BOT_TOKEN=your-discord-bot-token
DISCORD_DEFAULT_TOKEN_TYPE=Bot
CHAT_CHANNEL_ID=your-discord-channel-id
```

### 2. Build and Run

```bash
cd deploy
docker-compose up --build
```

### 3. Access Services

- **AI Ticket Service**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000

## Development

To run the service locally without Docker:

```bash
# From the project root
uv run --extra dev uvicorn ai_ticket_service.main:app --reload --port 8000
```

## API Usage

### Create a Ticket (Trello Backend)

```bash
curl -X POST http://localhost:8000/command \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "create a ticket for fixing the login bug",
    "system_prompt": "You are a helpful assistant that creates tickets",
    "backend": "trello"
  }'
```

### Create a Ticket (Google Tasks Backend)

```bash
curl -X POST http://localhost:8000/command \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "create a ticket for database optimization",
    "system_prompt": "You are a helpful assistant that creates tickets",
    "backend": "google_tasks"
  }'
```

## Monitoring

- Prometheus scrapes metrics from the AI service at `/metrics`
- Grafana can be configured to visualize these metrics
- Default Grafana credentials: admin/admin (change on first login)

## Stopping Services

```bash
docker-compose down
```

To remove volumes as well:

```bash
docker-compose down -v
```
