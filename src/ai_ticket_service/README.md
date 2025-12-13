# AI Ticket Service

FastAPI service that turns natural language into ticket operations by chaining an AI model with a pluggable ticket backend (Google Tasks or Trello).

## Endpoints
- `GET /health` – simple liveness check.
- `POST /command` – body:
  ```json
  {
    "user_input": "Create a ticket to add rate limiting to the public API.",
    "system_prompt": "You are a concise ticketing assistant.",
    "backend": "trello",
    "response_schema": null
  }
  ```
  Returns the AI-extracted command plus the ticket backend result.

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
- You can also pass `backend` in the `POST /command` payload to override per request.

## 📊 Telemetry & Monitoring (Live URLs)
* **Grafana Dashboard (Visuals):** [http://44.204.205.83:3000](http://44.204.205.83:3000)
  * *Login:* `admin` / `admin`
  * *View:* Real-time latency and error rate graphs.
* **Raw Metrics:** [http://44.204.205.83:8000/metrics](http://44.204.205.83:8000/metrics)
  * *Description:* Prometheus formatted metrics exposed by the AI Service.

## Testing
Run component tests for this service:
```bash
UV_CACHE_DIR=.uv_cache uv run --extra dev pytest src/ai_ticket_service/tests
```

