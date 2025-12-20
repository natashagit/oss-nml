# Testing Guide

The project uses pytest markers to keep unit, integration, and end-to-end tests organized.

Markers:
- `unit`: fast, isolated tests
- `integration`: component interaction tests
- `e2e`: end-to-end workflow tests
- `circleci`: CI-safe tests
- `local_credentials`: tests that need local auth files

Run tests:
```bash
# Unit tests
uv run pytest src/

# Integration tests
uv run pytest -m integration

# End-to-end tests (requires running service + chat creds)
uv run pytest -m e2e

# All tests except local credentials
uv run pytest src/ tests/ -m "not local_credentials"
```

Chat E2E requires `CHAT_CHANNEL_ID` and `DISCORD_BOT_TOKEN`.
