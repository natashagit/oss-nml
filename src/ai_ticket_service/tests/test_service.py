"""Unit tests for ai_ticket_service.main."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

from ai_ticket_service.main import app
from tickets_api import TicketStatus


class _FakeAIClient:
    def __init__(self, result: dict[str, Any]) -> None:
        self._result = result

    def generate_response(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return self._result


class _FakeTicketsClient:
    def __init__(self) -> None:
        self._ticket = SimpleNamespace(
            id="tid-123",
            title="Test Ticket",
            description="Desc",
            status=TicketStatus.OPEN,
            assignee=None,
        )

    def create_ticket(self, title: str, description: str) -> Ticket:
        self._ticket.title = title
        self._ticket.description = description
        return self._ticket

    def search_tickets(self, query: str | None = None, status: TicketStatus | None = None) -> list[Ticket]:
        del query, status
        return [self._ticket]

    def get_ticket(self, ticket_id: str) -> Ticket | None:
        return self._ticket if ticket_id == self._ticket.id else None

    def update_ticket(
        self,
        ticket_id: str,
        status: TicketStatus | None = None,
        title: str | None = None,
    ) -> Ticket:
        if title:
            self._ticket.title = title
        if status:
            self._ticket.status = status
        return self._ticket

    def delete_ticket(self, ticket_id: str) -> bool:
        return ticket_id == self._ticket.id


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


def test_command_create(monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    fake_ai = _FakeAIClient(
        {
            "intent": "create_ticket",
            "title": "New Ticket",
            "description": "Body",
        },
    )
    fake_tickets = _FakeTicketsClient()

    monkeypatch.setattr("ai_ticket_service.main.get_client", lambda: fake_ai)
    monkeypatch.setattr("ai_ticket_service.main.TicketsClient", lambda interactive=False: fake_tickets)

    response = client.post(
        "/command",
        json={
            "user_input": "create",
            "system_prompt": "prompt",
            "response_schema": {"type": "object"},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ai_result"]["intent"] == "create_ticket"
    assert data["ticket_result"]["title"] == "New Ticket"


def test_command_search(monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    fake_ai = _FakeAIClient(
        {
            "intent": "search_tickets",
            "query": "all",
            "status": "",
        },
    )
    fake_tickets = _FakeTicketsClient()

    monkeypatch.setattr("ai_ticket_service.main.get_client", lambda: fake_ai)
    monkeypatch.setattr("ai_ticket_service.main.TicketsClient", lambda interactive=False: fake_tickets)

    response = client.post(
        "/command",
        json={
            "user_input": "list",
            "system_prompt": "prompt",
            "response_schema": {"type": "object"},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["ticket_result"], list)
    assert data["ticket_result"][0]["id"] == "tid-123"


def test_command_get(monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    fake_ai = _FakeAIClient(
        {
            "intent": "get_ticket",
            "ticket_id": "tid-123",
        },
    )
    fake_tickets = _FakeTicketsClient()

    monkeypatch.setattr("ai_ticket_service.main.get_client", lambda: fake_ai)
    monkeypatch.setattr("ai_ticket_service.main.TicketsClient", lambda interactive=False: fake_tickets)

    response = client.post(
        "/command",
        json={
            "user_input": "get",
            "system_prompt": "prompt",
            "response_schema": {"type": "object"},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ticket_result"]["id"] == "tid-123"


def test_command_update(monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    fake_ai = _FakeAIClient(
        {
            "intent": "update_ticket",
            "ticket_id": "tid-123",
            "status": "closed",
            "title": "Updated",
        },
    )
    fake_tickets = _FakeTicketsClient()

    monkeypatch.setattr("ai_ticket_service.main.get_client", lambda: fake_ai)
    monkeypatch.setattr("ai_ticket_service.main.TicketsClient", lambda interactive=False: fake_tickets)

    response = client.post(
        "/command",
        json={
            "user_input": "update",
            "system_prompt": "prompt",
            "response_schema": {"type": "object"},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ticket_result"]["title"] == "Updated"
    assert data["ticket_result"]["status"] == "closed"


def test_command_delete(monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    fake_ai = _FakeAIClient(
        {
            "intent": "delete_ticket",
            "ticket_id": "tid-123",
        },
    )
    fake_tickets = _FakeTicketsClient()

    monkeypatch.setattr("ai_ticket_service.main.get_client", lambda: fake_ai)
    monkeypatch.setattr("ai_ticket_service.main.TicketsClient", lambda interactive=False: fake_tickets)

    response = client.post(
        "/command",
        json={
            "user_input": "delete",
            "system_prompt": "prompt",
            "response_schema": {"type": "object"},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ticket_result"]["deleted"] is True
