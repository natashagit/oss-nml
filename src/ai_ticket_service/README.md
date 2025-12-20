# Chat AI Ticket Orchestration

Live deployment: https://oss-nml.onrender.com/docs

FastAPI service that turns natural language into ticket operations by chaining an AI model with a
pluggable ticket backend (Google Tasks or Trello). It can also post the formatted response back
to a chat channel (Discord) through the shared chat client interface.

Workflow (high level):
User input goes to AI for intent extraction, then the ticket backend executes the action.
The AI formats the ticket results and the chat client posts the response to the channel.

## Endpoints
- `GET /health` - simple liveness check.
- `POST /chat/command` - body:
  ```json
  {
    "user_input": "Create a ticket to add rate limiting to the public API."
  }
  ```
  Returns the AI-extracted command, ticket backend result, and the chat post status.
Deployed docs: https://oss-nml.onrender.com/docs

## Configuration
Load environment variables (e.g., via `.env`) before running:

### Common
- `OPENAI_API_KEY` – API key for the AI provider.
- `TICKET_BACKEND` – `google_tasks` (default) or `trello`.

### Google Tasks backend
- `TASKS_CLIENT_ID`
- `TASKS_CLIENT_SECRET`
- `TASKS_REFRESH_TOKEN`
- `TASKS_TOKEN_URI` (default: `https://oauth2.googleapis.com/token`)
- `TASKS_INTERACTIVE` – `true` to allow interactive auth, else `false`.

### Trello backend
- `TRELLO_API_KEY`
- `TRELLO_API_SECRET`
- `TRELLO_TOKEN`
- `TRELLO_BOARD_ID`
- `REDIRECT_URI` (optional, default set to `http://localhost:8000/callback` if missing)

### Chat (Discord)
- `DISCORD_BOT_TOKEN`
- `CHAT_CHANNEL_ID` (or `DISCORD_CHANNEL_ID`)
- `DISCORD_DEFAULT_TOKEN_TYPE` (optional, default `Bot`)
- `CHAT_SYSTEM_PROMPT` (optional)
- `CHAT_USER_ID` (optional)

## Running the service
```bash
UV_CACHE_DIR=.uv_cache \
PYTHONPATH=src \
uv run --extra dev uvicorn ai_ticket_service.main:app --reload --port 8000
```
Then open `http://127.0.0.1:8000/docs` for the interactive API.

## Switching backends
- Default backend is `google_tasks`.
- Set `TICKET_BACKEND=trello` to use Trello.
- You can also pass `backend` in the `POST /chat/command` payload to override per request.

## 📊 Telemetry & Monitoring (Live URLs)
* **Grafana Dashboard (Visuals):** [http://3.239.197.228:3000/d/adbqk72/ai-ticket-service-telemetry?orgId=1](telemetry website)
  * *Login:* `admin` / `admin`
  * *View:* Real-time latency and error rate graphs.

## Testing
Run component tests for this service:
```bash
UV_CACHE_DIR=.uv_cache uv run --extra dev pytest src/ai_ticket_service/tests
```
