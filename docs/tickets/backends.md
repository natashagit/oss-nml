# Ticket Backends

The AI Ticket service supports multiple ticket providers behind the `tickets_api` contract.
Choose the backend with `TICKET_BACKEND`.

## Google Tasks
- `TICKET_BACKEND=google_tasks`
- `TASKS_CLIENT_ID`
- `TASKS_CLIENT_SECRET`
- `TASKS_REFRESH_TOKEN`
- `TASKS_TOKEN_URI` (default `https://oauth2.googleapis.com/token`)
- `TASKS_INTERACTIVE` (`true` for interactive auth)

## Trello
- `TICKET_BACKEND=trello`
- `TRELLO_API_KEY`
- `TRELLO_API_SECRET`
- `TRELLO_TOKEN`
- `TRELLO_BOARD_ID`
- `REDIRECT_URI` (optional)
