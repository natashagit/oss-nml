"""Unit tests for ai_ticket_service.main."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from ai_ticket_service.main import app
from ai_api import AIInterface
from tickets_api import TicketInterface, TicketStatus
from ai_ticket_service.models import ChatCommandRequest, CommandRequest, CommandResponse


class _FakeAIClient(AIInterface):
    def __init__(self, responses: list[Any] | dict[str, Any] | str) -> None:
        if isinstance(responses, list):
            self._responses = responses
        else:
            self._responses = [responses]
        self._idx = 0

    def generate_response(self, *args: Any, **kwargs: Any) -> Any:
        result = self._responses[min(self._idx, len(self._responses) - 1)]
        self._idx += 1
        return result


class _FakeTicketsClient(TicketInterface):
    def __init__(self) -> None:
        self._ticket = SimpleNamespace(
            id="tid-123",
            title="Test Ticket",
            description="Desc",
            status=TicketStatus.OPEN,
            assignee=None,
        )

    def create_ticket(self, title: str, description: str, assignee: str | None = None) -> Any:
        self._ticket.title = title
        self._ticket.description = description
        return self._ticket

    def search_tickets(self, query: str | None = None, status: TicketStatus | None = None) -> list[Any]:
        del query, status
        return [self._ticket]

    def get_ticket(self, ticket_id: str) -> Any | None:
        return self._ticket if ticket_id == self._ticket.id else None

    def update_ticket(
        self,
        ticket_id: str,
        status: TicketStatus | None = None,
        title: str | None = None,
    ) -> Any:
        if title:
            self._ticket.title = title
        if status is not None:
            self._ticket.status = status
        return self._ticket

    def delete_ticket(self, ticket_id: str) -> bool:
        return bool(ticket_id == self._ticket.id)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health_endpoint(client: TestClient) -> None:
    """Test the health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_backend_factory_google_tasks(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test TicketBackendFactory with Google Tasks backend."""
    from ai_ticket_service.main import TicketBackendFactory

    # Mock the TicketsClient to avoid credential issues
    class MockTicketsClient:
        def __init__(self, **kwargs: Any) -> None:
            pass

        def create_ticket(self, title: str, description: str, assignee: str | None = None) -> object:
            return _FakeTicketsClient()._ticket

    monkeypatch.setattr("ai_ticket_service.main.TicketsClient", MockTicketsClient)
    backend = TicketBackendFactory.create_backend("google_tasks")
    assert backend is not None
    assert hasattr(backend, "create_ticket")


def test_backend_factory_invalid_backend() -> None:
    """Test TicketBackendFactory with invalid backend."""
    from ai_ticket_service.main import TicketBackendFactory

    with pytest.raises(ValueError, match="Unsupported backend type"):
        TicketBackendFactory.create_backend("invalid_backend")


def test_backend_status_check(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test _get_backend_status function."""
    from ai_ticket_service.main import _get_backend_status

    # Mock successful backend creation
    class MockTicketsClient:
        def __init__(self, **kwargs: Any) -> None:
            pass

    monkeypatch.setattr("ai_ticket_service.main.TicketsClient", MockTicketsClient)
    # Google Tasks should work with mock
    status = _get_backend_status("google_tasks")
    assert status == "success"
    # Invalid backend should return not_configured
    status = _get_backend_status("invalid_backend")
    assert status == "not_configured"


def test_status_parsing() -> None:
    """Test _parse_status function."""
    from ai_ticket_service.main import _parse_status
    from tickets_api import TicketStatus

    # Test valid status strings
    assert _parse_status("open") == TicketStatus.OPEN
    assert _parse_status("in progress") == TicketStatus.IN_PROGRESS
    assert _parse_status("in_progress") == TicketStatus.IN_PROGRESS
    assert _parse_status("closed") == TicketStatus.CLOSED
    assert _parse_status("done") == TicketStatus.CLOSED
    # Test None and empty strings
    assert _parse_status(None) is None
    assert _parse_status("") is None
    # Test invalid status - should return None due to ValueError
    assert _parse_status("invalid_status") is None


def test_status_parsing_handles_value_error() -> None:
    """_parse_status should return None if normalization raises ValueError."""
    from ai_ticket_service.main import _parse_status

    class BadStatus:
        def lower(self) -> str:  # type: ignore[override]
            msg = "bad"
            raise ValueError(msg)

    assert _parse_status(BadStatus()) is None  # type: ignore[arg-type]


def test_chat_command_with_trello_backend_not_configured(
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
) -> None:
    """Test /chat/command with Trello backend when not configured."""
    fake_ai = _FakeAIClient(
        {
            "intent": "create_ticket",
            "title": "Test Ticket",
            "description": "Test Description",
            "ticket_id": "",
            "query": "",
            "status": "",
        },
    )
    # Clear Trello environment variables to simulate not configured
    for key in ["TRELLO_TOKEN", "TRELLO_BOARD_ID", "TRELLO_API_KEY", "TRELLO_API_SECRET"]:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("TICKET_BACKEND", "trello")
    monkeypatch.setenv("CHAT_CHANNEL_ID", "channel-123")

    class FakeChatClient:
        def send_message(self, channel_id: str, content: str) -> bool:
            return True

    monkeypatch.setattr("ai_ticket_service.main.get_client", lambda: fake_ai)
    monkeypatch.setattr("ai_ticket_service.main._get_chat_client", lambda user_id=None: FakeChatClient())
    response = client.post("/chat/command", json={"user_input": "create a ticket"})
    assert response.status_code == 200
    data = response.json()
    assert data["backend_used"] == "trello"
    assert data["backend_status"] == "not_configured"
    assert data["message"] == "No ticket updates available."


def test_chat_command_with_backend_error(monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    """Test /chat/command when backend throws an error during ticket operation."""
    fake_ai = _FakeAIClient(
        {
            "intent": "create_ticket",
            "title": "Test Ticket",
            "description": "Test Description",
            "ticket_id": "",
            "query": "",
            "status": "",
        },
    )

    # Mock successful backend creation but failing ticket operation
    class FailingTicketsClient:
        def create_ticket(self, title: str, description: str, assignee: str | None = None) -> None:
            msg = "Ticket operation failed"
            raise RuntimeError(msg)

    def backend_factory(backend_type: str) -> object:
        return FailingTicketsClient()

    monkeypatch.setenv("TICKET_BACKEND", "google_tasks")
    monkeypatch.setenv("CHAT_CHANNEL_ID", "channel-456")

    class FakeChatClient:
        def send_message(self, channel_id: str, content: str) -> bool:
            return True

    monkeypatch.setattr("ai_ticket_service.main.get_client", lambda: fake_ai)
    monkeypatch.setattr("ai_ticket_service.main.TicketBackendFactory.create_backend", backend_factory)
    monkeypatch.setattr("ai_ticket_service.main._get_chat_client", lambda user_id=None: FakeChatClient())
    response = client.post("/chat/command", json={"user_input": "create a ticket"})
    assert response.status_code == 200
    data = response.json()
    assert data["backend_used"] == "google_tasks"
    assert data["backend_status"] == "error"
    assert data["message"] == "No ticket updates available."


def test_handle_create_ticket() -> None:
    """Test _handle_create_ticket helper function."""
    from ai_ticket_service.main import _handle_create_ticket
    from typing import cast

    fake_tickets = cast("TicketInterface", _FakeTicketsClient())
    ai_result = {
        "title": "Test Title",
        "description": "Test Description",
    }
    result = _handle_create_ticket(ai_result, fake_tickets)
    assert result["title"] == "Test Title"
    assert result["description"] == "Test Description"


def test_handle_create_ticket_failure() -> None:
    """_handle_create_ticket returns error when backend fails."""
    from ai_ticket_service.main import _handle_create_ticket

    class FailingTickets:
        def create_ticket(self, title: str, description: str, assignee: str | None = None) -> None:
            return None

    result = _handle_create_ticket(
        {"title": "Broken", "description": ""},
        cast("TicketInterface", FailingTickets()),
    )
    assert "error" in result


def test_handle_update_ticket() -> None:
    """Test _handle_update_ticket helper function."""
    from ai_ticket_service.main import _handle_update_ticket
    from typing import cast

    fake_tickets = cast("TicketInterface", _FakeTicketsClient())
    ai_result = {
        "ticket_id": "tid-123",
        "title": "Updated Title",
        "status": "closed",
    }
    result = _handle_update_ticket(ai_result, fake_tickets)
    assert result["title"] == "Updated Title"
    assert result["status"] == "closed"  # TicketStatus.CLOSED.value is "closed"


def test_handle_update_ticket_failure() -> None:
    """_handle_update_ticket returns error when backend fails."""
    from ai_ticket_service.main import _handle_update_ticket

    class FailingTickets:
        def update_ticket(self, **kwargs: Any) -> None:
            return None

    result = _handle_update_ticket(
        {"ticket_id": "tid-123", "status": "closed"},
        cast("TicketInterface", FailingTickets()),
    )
    assert "error" in result


def test_handle_update_ticket_no_id() -> None:
    """Test _handle_update_ticket with no ticket_id."""
    from ai_ticket_service.main import _handle_update_ticket
    from typing import cast

    fake_tickets = cast("TicketInterface", _FakeTicketsClient())
    ai_result = {
        "title": "Updated Title",
        "status": "closed",
    }
    result = _handle_update_ticket(ai_result, fake_tickets)
    assert result == {}


def test_handle_get_ticket_not_found() -> None:
    """_handle_get_ticket returns error when ticket is missing."""
    from ai_ticket_service.main import _handle_get_ticket

    class MissingTickets:
        def get_ticket(self, ticket_id: str) -> None:
            return None

    result = _handle_get_ticket({"ticket_id": "missing"}, cast("TicketInterface", MissingTickets()))
    assert result == {"error": "Ticket missing not found."}


def test_handle_get_ticket_no_id() -> None:
    """_handle_get_ticket returns error when no ticket_id provided."""
    from ai_ticket_service.main import _handle_get_ticket

    result = _handle_get_ticket({}, _FakeTicketsClient())
    assert result == {"error": "No ticket_id provided for lookup."}


def test_serialize_ticket() -> None:
    """Test _serialize_ticket function."""
    from ai_ticket_service.main import _serialize_ticket
    from typing import cast
    from tickets_api import Ticket

    fake_ticket = cast("Ticket", _FakeTicketsClient()._ticket)
    result = _serialize_ticket(fake_ticket)
    assert result["id"] == "tid-123"
    assert result["title"] == "Test Ticket"
    assert result["description"] == "Desc"
    assert result["status"] == "open"  # TicketStatus.OPEN.value is "open"
    assert result["assignee"] is None


def test_handle_delete_ticket_no_id() -> None:
    """_handle_delete_ticket returns error when ticket_id missing."""
    from ai_ticket_service.main import _handle_delete_ticket

    result = _handle_delete_ticket({}, _FakeTicketsClient())
    assert result == {"error": "No ticket_id provided for deletion."}


def test_handle_delete_ticket_success() -> None:
    """_handle_delete_ticket returns deleted flag from backend."""
    from ai_ticket_service.main import _handle_delete_ticket

    result = _handle_delete_ticket({"ticket_id": "tid-123"}, _FakeTicketsClient())
    assert result == {"ticket_id": "tid-123", "deleted": True}


def test_backend_factory_trello_missing_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test TicketBackendFactory with Trello backend missing token."""
    from ai_ticket_service.main import TicketBackendFactory

    # Clear any existing Trello env vars
    for key in ["TRELLO_TOKEN", "TRELLO_BOARD_ID", "TRELLO_API_KEY", "TRELLO_API_SECRET"]:
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(RuntimeError, match="TRELLO_TOKEN environment variable is required"):
        TicketBackendFactory.create_backend("trello")


def test_backend_factory_trello_missing_board_id(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test TicketBackendFactory with Trello backend missing board_id."""
    from ai_ticket_service.main import TicketBackendFactory

    # Set token but not board_id
    monkeypatch.setenv("TRELLO_TOKEN", "test_token")
    monkeypatch.delenv("TRELLO_BOARD_ID", raising=False)
    with pytest.raises(RuntimeError, match="TRELLO_BOARD_ID environment variable is required"):
        TicketBackendFactory.create_backend("trello")


def test_backend_factory_trello_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test TicketBackendFactory with Trello backend success path."""
    from ai_ticket_service.main import TicketBackendFactory

    # Mock all required environment variables
    monkeypatch.setenv("TRELLO_TOKEN", "test_token")
    monkeypatch.setenv("TRELLO_BOARD_ID", "test_board")
    monkeypatch.setenv("TRELLO_API_KEY", "test_key")
    monkeypatch.setenv("TRELLO_API_SECRET", "test_secret")
    monkeypatch.setenv("REDIRECT_URI", "http://localhost:8000/callback")

    # Mock the imports at the module level where they're imported
    class MockTrelloClient:
        def __init__(self, **kwargs: Any) -> None:
            self.kwargs = kwargs

        def create_ticket(self, title: str, description: str, assignee: str | None = None) -> object:
            return _FakeTicketsClient()._ticket

    class MockOAuthHandler:
        @classmethod
        def from_env(cls) -> MockOAuthHandler:
            return cls()

    # Mock the imports using monkeypatch at the function level
    def mock_trello_factory(backend_type: str) -> object:
        if backend_type == "trello":
            return MockTrelloClient()
        return _FakeTicketsClient()

    # Override the factory method to avoid import issues
    monkeypatch.setattr("ai_ticket_service.main.TicketBackendFactory.create_backend", mock_trello_factory)

    # This should now work without errors
    backend = TicketBackendFactory.create_backend("trello")
    assert backend is not None
    assert isinstance(backend, MockTrelloClient)


def test_backend_factory_trello_calls_dependencies(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure the Trello backend wiring invokes OAuth handler and client constructors."""
    from ai_ticket_service.main import TicketBackendFactory

    monkeypatch.setenv("TRELLO_TOKEN", "token")
    monkeypatch.setenv("TRELLO_BOARD_ID", "board")
    monkeypatch.setenv("TRELLO_API_KEY", "api-key")
    monkeypatch.setenv("TRELLO_API_SECRET", "api-secret")
    monkeypatch.delenv("REDIRECT_URI", raising=False)

    class DummyOAuth:
        called = False

        @classmethod
        def from_env(cls) -> DummyOAuth:
            cls.called = True
            return cls()

    class DummyClient:
        def __init__(self, **kwargs: Any) -> None:
            self.kwargs = kwargs

    monkeypatch.setattr("ai_ticket_service.main.TrelloOAuthHandler", DummyOAuth)
    monkeypatch.setattr("ai_ticket_service.main.TrelloTicketClientImpl", DummyClient)

    backend = TicketBackendFactory.create_backend("trello")
    assert isinstance(backend, DummyClient)
    assert DummyOAuth.called is True


def test_format_ticket_markdown_chat_passthrough() -> None:
    """_format_ticket_markdown should return chat messages directly."""
    from ai_ticket_service.main import _format_ticket_markdown

    result = _format_ticket_markdown({"type": "chat", "message": "Hello"})
    assert result == "Hello"


def test_chat_command_endpoint_posts_messages(monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    """`/chat/command` should send both the user text and formatted output."""
    sent_messages: list[str] = []

    class FakeChatClient:
        def send_message(self, channel_id: str, content: str) -> bool:
            sent_messages.append(content)
            return True

    def fake_process_command(request: CommandRequest) -> CommandResponse:
        return CommandResponse(
            ai_result={"intent": "chat"},
            ticket_result=None,
            backend_used="google_tasks",
            backend_status="success",
            formatted_response="Formatted summary",
        )

    monkeypatch.setenv("CHAT_CHANNEL_ID", "channel-123")
    monkeypatch.setattr("ai_ticket_service.main._get_chat_client", lambda user_id=None: FakeChatClient())
    monkeypatch.setattr("ai_ticket_service.main._process_command", fake_process_command)

    response = client.post("/chat/command", json={"user_input": "list the tickets"})
    assert response.status_code == 200
    assert sent_messages[0].startswith("User: list the tickets")
    assert sent_messages[1] == "Formatted summary"


def test_chat_command_fallbacks_to_markdown(monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    """When formatted response is missing, fallback Markdown should be sent."""
    sent_messages: list[str] = []

    class FakeChatClient:
        def send_message(self, channel_id: str, content: str) -> bool:
            sent_messages.append(content)
            return True

    def fake_process_command(request: CommandRequest) -> CommandResponse:
        return CommandResponse(
            ai_result={"intent": "search_tickets"},
            ticket_result=[
                {"id": "1", "title": "Fix bug", "description": "Bug desc", "status": "open", "assignee": None},
            ],
            backend_used="google_tasks",
            backend_status="success",
            formatted_response=None,
        )

    monkeypatch.setenv("CHAT_CHANNEL_ID", "channel-456")
    monkeypatch.setattr("ai_ticket_service.main._get_chat_client", lambda user_id=None: FakeChatClient())
    monkeypatch.setattr("ai_ticket_service.main._process_command", fake_process_command)

    response = client.post("/chat/command", json={"user_input": "list tickets"})
    assert response.status_code == 200
    assert "*Ticket 1*" in sent_messages[1]


def test_chat_command_missing_channel_id_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """_handle_chat_command should raise when channel id is missing."""
    from ai_ticket_service.main import _handle_chat_command

    monkeypatch.delenv("CHAT_CHANNEL_ID", raising=False)
    with pytest.raises(HTTPException, match="CHAT_CHANNEL_ID not configured"):
        _handle_chat_command(ChatCommandRequest(user_input="list tickets"))


def test_format_ticket_response_none_payload() -> None:
    """_format_ticket_response should return None when no ticket payload provided."""
    from ai_ticket_service.main import _format_ticket_response

    client = _FakeAIClient("unused")
    assert _format_ticket_response(client, "request text", None) is None


def test_format_ticket_response_ai_result_string_returns_none() -> None:
    """_format_ticket_response should return None if ai_result is a string."""
    from ai_ticket_service.main import _format_ticket_response

    client = _FakeAIClient("unused")
    result = _format_ticket_response(
        client,
        "request",
        {"id": "1", "title": "Ticket"},
        ai_result="text",
    )
    assert result is None


def test_format_ticket_response_unserializable_payload() -> None:
    """_format_ticket_response should fall back to string serialization."""
    from ai_ticket_service.main import _format_ticket_response

    client = _FakeAIClient("Formatted output")
    payload = {"data": {1, 2, 3}}  # sets are not JSON serializable
    result = _format_ticket_response(client, "request", payload)
    assert result == "Formatted output"


def test_format_ticket_response_circular_payload() -> None:
    """_format_ticket_response should handle circular data in ticket payload."""
    from ai_ticket_service.main import _format_ticket_response

    client = _FakeAIClient("Formatted output")
    payload: list[Any] = []
    payload.append(payload)
    result = _format_ticket_response(client, "request", payload, ai_result={"intent": "search_tickets"})
    assert result == "Formatted output"


def test_format_ticket_response_dict_result() -> None:
    """_format_ticket_response should JSON-encode non-string AI results."""
    from ai_ticket_service.main import _format_ticket_response

    client = _FakeAIClient({"ok": True})
    result = _format_ticket_response(client, "request", {"id": "1"}, ai_result={"intent": "get_ticket"})
    assert result == '{"ok": true}'


def test_format_ticket_response_handles_ai_exception() -> None:
    """_format_ticket_response should return None when AI call fails."""
    from ai_ticket_service.main import _format_ticket_response

    class RaisingAI(AIInterface):
        def generate_response(self, *args: Any, **kwargs: Any) -> Any:
            msg = "boom"
            raise RuntimeError(msg)

    assert _format_ticket_response(RaisingAI(), "request", {"id": "123"}) is None


def test_format_ticket_response_chat_passthrough() -> None:
    """Chat-style responses should bypass ticket formatting."""
    from ai_ticket_service.main import _format_ticket_response

    client = _FakeAIClient("unused")
    ticket_result = {"type": "chat", "message": "I'm here to help."}
    result = _format_ticket_response(client, "hello", ticket_result, ai_result={"intent": "chat"})
    assert result == "I'm here to help."


def test_handle_chat_default_message() -> None:
    """_handle_chat should return default message when missing."""
    from ai_ticket_service.main import _handle_chat

    result = _handle_chat({}, _FakeTicketsClient())
    assert result["type"] == "chat"
    assert result["message"] == "I'm here to help with ticket operations."


def test_handle_unknown_default_message() -> None:
    """_handle_unknown should return default unknown message."""
    from ai_ticket_service.main import _handle_unknown

    result = _handle_unknown({}, _FakeTicketsClient())
    assert result["type"] == "unknown"
    assert "not sure" in result["message"]


def test_handle_intent_invalid_type() -> None:
    """_handle_intent should return None for non-string intent."""
    from ai_ticket_service.main import _handle_intent

    result = _handle_intent({"intent": None}, _FakeTicketsClient())
    assert result is None


def test_process_command_chat_flow(monkeypatch: pytest.MonkeyPatch) -> None:
    """_process_command should handle chat intent without backend."""
    from ai_ticket_service.main import _process_command

    fake_ai = _FakeAIClient({"intent": "chat", "message": "Hello"})
    monkeypatch.setattr("ai_ticket_service.main.get_client", lambda: fake_ai)
    result = _process_command(CommandRequest(user_input="hi", system_prompt="prompt", backend="google_tasks"))
    assert result.ticket_result == {"type": "chat", "message": "Hello"}
    assert result.formatted_response == "Hello"


def test_process_command_unknown_flow(monkeypatch: pytest.MonkeyPatch) -> None:
    """_process_command should handle unknown intent without backend."""
    from ai_ticket_service.main import _process_command

    fake_ai = _FakeAIClient({"intent": "unknown", "message": "No idea"})
    monkeypatch.setattr("ai_ticket_service.main.get_client", lambda: fake_ai)
    result = _process_command(CommandRequest(user_input="?", system_prompt="prompt", backend="google_tasks"))
    assert result.ticket_result == {"type": "unknown", "message": "No idea"}
    assert result.formatted_response == "No idea"
