"""Tests for the AI ticket adapter."""

from __future__ import annotations

import pytest

from ai_ticket_adapter import TicketOrchestrationAdapter
from ai_ticket_service_client.models import CommandResponse


def test_command_returns_response(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = CommandResponse.from_dict(
        {
            "ai_result": {"intent": "create_ticket"},
            "ticket_result": {"id": "1"},
            "backend_used": "google_tasks",
            "backend_status": "success",
        },
    )

    def fake_sync(*args: object, **kwargs: object) -> CommandResponse:
        del args, kwargs
        return expected

    monkeypatch.setattr(
        "ai_ticket_adapter.client_impl.sync",
        fake_sync,
    )

    adapter = TicketOrchestrationAdapter(base_url="http://test")
    result = adapter.command("hi", system_prompt="prompt")
    assert result == expected


def test_raw_response_raises_on_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "ai_ticket_adapter.client_impl.sync",
        lambda *args, **kwargs: None,
    )

    adapter = TicketOrchestrationAdapter(base_url="http://test")
    with pytest.raises(RuntimeError):
        adapter.raw_response("hi", system_prompt="prompt")
