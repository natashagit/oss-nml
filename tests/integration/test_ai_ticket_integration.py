"""Integration-style tests for the AI Ticket orchestration FastAPI app."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

from ai_ticket_service.main import app
from tickets_api import TicketStatus


class _FakeAI:
    def __init__(self, responses: list[Any]) -> None:
        self._responses = responses
        self._idx = 0

    def generate_response(self, *args: Any, **kwargs: Any) -> Any:
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


class _FakeChatClient:
    def __init__(self) -> None:
        self.messages: list[tuple[str, str]] = []

    def send_message(self, channel_id: str, content: str) -> None:
        self.messages.append((channel_id, content))


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_chat_command_flow(monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    fake_ai = _FakeAI(
        [
            {
                "intent": "search_tickets",
                "title": "",
                "description": "",
                "ticket_id": "",
                "query": "login",
                "status": "",
            },
            "Ticket 1: Login issue.",
        ],
    )
    fake_tickets = _FakeTickets()
    fake_chat = _FakeChatClient()

    monkeypatch.setattr("ai_ticket_service.main.get_client", lambda: fake_ai)
    monkeypatch.setattr("ai_ticket_service.main.TicketBackendFactory.create_backend", lambda backend_type: fake_tickets)
    monkeypatch.setattr("ai_ticket_service.main.chat_client_api.get_client", lambda user_id=None: fake_chat)
    monkeypatch.setenv("CHAT_CHANNEL_ID", "chan-123")

    response = client.post("/chat/command", json={"user_input": "list tickets about login"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "posted"
    assert data["channel_id"] == "chan-123"
    assert data["message"] == "Ticket 1: Login issue."
    assert fake_chat.messages == [
        ("chan-123", "User: list tickets about login"),
        ("chan-123", "Ticket 1: Login issue."),
    ]
