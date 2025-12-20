# OSS-NML: Chat AI Ticket Orchestration

Live deployment: https://oss-nml.onrender.com/docs

This repository is a `uv` workspace for the HW3 system integration. It wires a chat client
(Discord), an AI router, and a ticket backend into a single pipeline:

Chat -> AI intent extraction -> Ticket backend -> AI formatting -> Chat response

## What's included

- **ai_ticket_service**: FastAPI orchestration service (`/chat/command`, `/health`).
- **tickets_api + tickets_client_impl**: Ticket interface + Google Tasks implementation.
- **trello_ticket_impl**: Trello backend (imported as a dependency).
- **chat_client_api + discord_client_impl**: Chat abstraction + Discord implementation.
- **ai_api + openai_impl**: AI contract + OpenAI implementation.
- **ai_ticket_adapter + ai_ticket_service_client**: Adapter + generated client for HTTP calls.

Older HW2/HW1 stacks (AI service, mail service) remain in `src/` but are not required for HW3.

## API

- `GET /health` - liveness check.
- `POST /chat/command` - sends the user input through AI + ticket backend and posts to chat.
Deployed docs: https://oss-nml.onrender.com/docs

Request body:
```json
{
  "user_input": "List all tickets"
}
```

Response body (example):
```json
{
  "status": "posted",
  "channel_id": "1234567890",
  "backend_used": "google_tasks",
  "backend_status": "success",
  "message": "Found 2 ticket(s)..."
}
```

## Configuration

Create a `.env` file (or export env vars) with what you need for your selected backend.

### AI
- `OPENAI_API_KEY`

### Ticket backend
Common:
- `TICKET_BACKEND=google_tasks` or `trello`

Google Tasks:
- `TASKS_CLIENT_ID`
- `TASKS_CLIENT_SECRET`
- `TASKS_REFRESH_TOKEN`
- `TASKS_TOKEN_URI` (default: `https://oauth2.googleapis.com/token`)
- `TASKS_INTERACTIVE` (`true` to allow interactive OAuth)

Trello:
- `TRELLO_API_KEY`
- `TRELLO_API_SECRET`
- `TRELLO_TOKEN`
- `TRELLO_BOARD_ID`
- `REDIRECT_URI` (optional, default `http://localhost:8000/callback`)

### Chat (Discord)
- `DISCORD_BOT_TOKEN`
- `CHAT_CHANNEL_ID` (or `DISCORD_CHANNEL_ID`)
- `DISCORD_DEFAULT_TOKEN_TYPE` (optional, default `Bot`)
- `CHAT_SYSTEM_PROMPT` (optional)
- `CHAT_USER_ID` (optional, used for auth lookup)

### Test helpers
- `AI_TICKET_SERVICE_URL` (used by adapter/e2e tests, default `http://127.0.0.1:8000`)

## Run locally

```bash
uv sync --all-packages --extra dev
source .venv/bin/activate

UV_CACHE_DIR=.uv_cache PYTHONPATH=src \
uv run --extra dev uvicorn ai_ticket_service.main:app --reload --port 8000
```

Try it from another terminal:
```bash
curl -X POST http://127.0.0.1:8000/chat/command \
  -H "Content-Type: application/json" \
  -d '{"user_input":"List all tickets"}'
```

Demo via adapter (uses `main.py`):
```bash
TICKET_BACKEND=google_tasks uv run python main.py
```

## Testing

```bash
# Unit tests (fast, no external deps)
uv run pytest src/

# Integration tests (mocked AI/tickets/chat)
uv run pytest -m integration

# End-to-end tests (requires running service + chat creds)
uv run pytest -m e2e

# Full suite excluding tests that need local credentials
uv run pytest src/ tests/ -m "not local_credentials"
```

## Telemetry & Deployment

- Metrics are exposed at `/metrics` (Prometheus format) by `prometheus_fastapi_instrumentator`.
- `deploy/` contains a Dockerfile, docker-compose, and Prometheus config for local monitoring.
- `terraform/main.tf` provisions an AWS EC2 host for the app + Grafana/Prometheus stack.

## Repository layout (key paths)

- `src/ai_ticket_service/` - orchestration service
- `src/tickets_api/` - ticket interface
- `src/tickets_client_impl/` - Google Tasks backend
- `src/chat_client_api/` - chat interface
- `src/discord_client_impl/` - Discord implementation
- `tests/integration/` - integration tests
- `tests/e2e/` - end-to-end tests
