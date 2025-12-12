"""Integration-style tests for the AI Ticket orchestration FastAPI app."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

from ai_ticket_service.main import app
from tickets_api import TicketStatus


class _FakeAI:
    def __init__(self, responses: list[dict[str, Any]]) -> None:
        self._responses = responses
        self._idx = 0

    def generate_response(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        del args, kwargs
        result = self._responses[self._idx]
        # cycle through provided responses
        self._idx = min(self._idx + 1, len(self._responses) - 1)
        return result


class _FakeTickets:
    def __init__(self) -> None:
        self._ticket = SimpleNamespace(
            id="tid-xyz",
            title="Initial",
            description="Initial desc",
            status=TicketStatus.OPEN,
            assignee=None,
        )
        self.deleted = False

    def create_ticket(self, title: str, description: str, assignee: str | None = None) -> Any:
        del assignee
        self._ticket.title = title
        self._ticket.description = description
        return self._ticket

    def get_ticket(self, ticket_id: str) -> Any | None:
        return self._ticket if ticket_id == self._ticket.id else None

    def search_tickets(self, query: str | None = None, status: TicketStatus | None = None) -> list[Any]:
        del query, status
        return [self._ticket]

    def update_ticket(self, ticket_id: str, status: TicketStatus | None = None, title: str | None = None) -> Any:
        if ticket_id != self._ticket.id:
            return self._ticket
        if title:
            self._ticket.title = title
        if status:
            self._ticket.status = status
        return self._ticket

    def delete_ticket(self, ticket_id: str) -> bool:
        self.deleted = self.deleted or ticket_id == self._ticket.id
        return self.deleted


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


def test_create_and_get_flow(monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    fake_ai = _FakeAI(
        [
            {
                "intent": "create_ticket",
                "title": "New Ticket",
                "description": "New Desc",
            },
            {
                "intent": "get_ticket",
                "ticket_id": "tid-xyz",
            },
        ],
    )
    fake_tickets = _FakeTickets()

    monkeypatch.setattr("ai_ticket_service.main.get_client", lambda: fake_ai)
    monkeypatch.setattr("ai_ticket_service.main.TicketsClient", lambda interactive=False: fake_tickets)

    # Create
    create_resp = client.post(
        "/command",
        json={"user_input": "create", "system_prompt": "prompt", "response_schema": {"type": "object"}},
    )
    assert create_resp.status_code == 200
    data = create_resp.json()
    assert data["ticket_result"]["id"] == "tid-xyz"
    assert data["ticket_result"]["title"] == "New Ticket"

    # Get
    get_resp = client.post(
        "/command",
        json={"user_input": "get it", "system_prompt": "prompt", "response_schema": {"type": "object"}},
    )
    assert get_resp.status_code == 200
    get_data = get_resp.json()
    assert get_data["ticket_result"]["id"] == "tid-xyz"


def test_update_and_delete_flow(monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    fake_ai = _FakeAI(
        [
            {
                "intent": "update_ticket",
                "ticket_id": "tid-xyz",
                "title": "Updated",
                "status": "closed",
            },
            {
                "intent": "delete_ticket",
                "ticket_id": "tid-xyz",
            },
        ],
    )
    fake_tickets = _FakeTickets()

    monkeypatch.setattr("ai_ticket_service.main.get_client", lambda: fake_ai)
    monkeypatch.setattr("ai_ticket_service.main.TicketsClient", lambda interactive=False: fake_tickets)

    # Update
    upd_resp = client.post(
        "/command",
        json={"user_input": "update", "system_prompt": "prompt", "response_schema": {"type": "object"}},
    )
    assert upd_resp.status_code == 200
    upd_data = upd_resp.json()
    assert upd_data["ticket_result"]["title"] == "Updated"
    assert upd_data["ticket_result"]["status"] == "closed"

    # Delete
    del_resp = client.post(
        "/command",
        json={"user_input": "delete", "system_prompt": "prompt", "response_schema": {"type": "object"}},
    )
    assert del_resp.status_code == 200
    del_data = del_resp.json()
    assert del_data["ticket_result"]["deleted"] is True
