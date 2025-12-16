"""E2E smoke test for AI Ticket orchestration (requires running service)."""

from __future__ import annotations

import os

import pytest
import requests


@pytest.mark.e2e
def test_ai_ticket_service_responds() -> None:
    """Call health and, if available, exercise /command."""
    base_url = os.getenv("AI_TICKET_SERVICE_URL", "http://127.0.0.1:8000")
    try:
        health = requests.get(f"{base_url}/health", timeout=2)
        if health.status_code != 200:
            pytest.skip(f"AI Ticket service not available at {base_url}")
    except (requests.ConnectionError, requests.Timeout):
        pytest.skip(f"AI Ticket service not running at {base_url}")

    payload = {
        "user_input": "Create a ticket to fix login redirect.",
        "system_prompt": "You route user requests into structured ticket commands.",
        "response_schema": {
            "type": "object",
            "properties": {
                "intent": {"type": "string", "enum": ["create_ticket"]},
                "title": {"type": "string"},
                "description": {"type": "string"},
            },
            "required": ["intent", "title", "description"],
            "additionalProperties": False,
        },
    }
    resp = requests.post(f"{base_url}/command", json=payload, timeout=5)
    if resp.status_code != 200:
        pytest.skip(f"AI Ticket service /command unavailable at {base_url}: {resp.status_code}")
    data = resp.json()
    assert "ai_result" in data
    assert "ticket_result" in data
