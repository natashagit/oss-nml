# OSS-NML: AI Ticket Orchestration

This project delivers a chat-first ticketing workflow: user input goes to an AI router, the ticket
backend executes the action, and the formatted response is posted back to chat.

Live docs: https://oss-nml.onrender.com/docs

## Highlights

- Chat integration via Discord using the shared `chat_client_api`.
- Ticket backends via a shared `tickets_api` contract (Google Tasks or Trello).
- AI intent extraction and formatting via `ai_api` with OpenAI implementation.
- Metrics exposed at `/metrics` with Grafana dashboards for latency and error rate.
