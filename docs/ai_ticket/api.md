# API

## POST /chat/command

Request:
```json
{
  "user_input": "List all tickets"
}
```

Response (example):
```json
{
  "status": "posted",
  "channel_id": "1234567890",
  "backend_used": "google_tasks",
  "backend_status": "success",
  "message": "Found 2 ticket(s)..."
}
```

## GET /health

Response:
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```
