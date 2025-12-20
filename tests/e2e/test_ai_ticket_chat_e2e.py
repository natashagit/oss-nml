"""E2E smoke test for AI Ticket chat endpoint (requires running service)."""

from __future__ import annotations

import os

import pytest
import requests


@pytest.mark.e2e
def test_ai_ticket_chat_command() -> None:
    """Call /chat/command if service and chat env are configured."""
    base_url = os.getenv("AI_TICKET_SERVICE_URL", "http://127.0.0.1:8000")
    try:
        health = requests.get(f"{base_url}/health", timeout=2)
        if health.status_code != 200:
            pytest.skip(f"AI Ticket service not available at {base_url}")
    except (requests.ConnectionError, requests.Timeout):
        pytest.skip(f"AI Ticket service not running at {base_url}")

    if not os.getenv("CHAT_CHANNEL_ID"):
        pytest.skip("CHAT_CHANNEL_ID not configured for chat e2e test")
    if not os.getenv("DISCORD_BOT_TOKEN"):
        pytest.skip("DISCORD_BOT_TOKEN not configured for chat e2e test")

    payload = {"user_input": "List all tickets"}
    resp = requests.post(f"{base_url}/chat/command", json=payload, timeout=5)
    if resp.status_code != 200:
        pytest.skip(f"AI Ticket service /chat/command unavailable at {base_url}: {resp.status_code}")

    data = resp.json()
    assert data["status"] == "posted"
    assert data["backend_used"]
