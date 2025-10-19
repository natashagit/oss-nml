"""Unit tests for FastAPI mail_client_service.

These tests:
- Use FastAPI's dependency override mechanism to inject a MagicMock
  instead of the real Gmail client.
- Verify request handling, response models, and error handling for all endpoints.
"""

from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from mail_client_service.dependencies import get_mail_client
from mail_client_service.main import app

# Create a TestClient for the FastAPI app
client = TestClient(app)

# HTTP status codes
HTTP_200_OK = 200
HTTP_404_NOT_FOUND = 404


@pytest.fixture
def mock_client() -> Generator[MagicMock, None, None]:
    """Create a MagicMock Gmail client and override the dependency.

    So FastAPI endpoints use it instead of the real Gmail client.
    """
    mock_instance = MagicMock()

    # Override the FastAPI dependency with our MagicMock
    app.dependency_overrides[get_mail_client] = lambda: mock_instance

    yield mock_instance

    # Clear overrides after each test to avoid leakage between tests
    app.dependency_overrides.clear()


def test_get_messages(mock_client: Any) -> None:
    """Test GET /messages returns a list of message summaries."""
    mock_client.get_messages.return_value = [
        MagicMock(
            id="m1",
            subject="Hello",
            from_="x@y.com",
            to="y@z.com",
            date="2025-10-01",
            body="Hi",
        ),
    ]

    resp = client.get("/messages")
    assert resp.status_code == HTTP_200_OK

    data = resp.json()
    assert isinstance(data, list)
    assert data[0]["id"] == "m1"
    assert data[0]["subject"] == "Hello"

    mock_client.get_messages.assert_called_once()


def test_get_single_message(mock_client: Any) -> None:
    """Test GET /messages/{id} returns full message detail."""
    mock_client.get_message.return_value = MagicMock(
        id="m1",
        subject="UnitTest",
        from_="a@b.com",
        to="z@b.com",
        date="2025-10-01",
        body="Body text",
    )

    resp = client.get("/messages/m1")
    assert resp.status_code == HTTP_200_OK

    data = resp.json()
    assert data["id"] == "m1"
    assert data["subject"] == "UnitTest"

    mock_client.get_message.assert_called_once_with("m1")


def test_delete_message(mock_client: Any) -> None:
    """Test DELETE /messages/{id} deletes a message successfully."""
    mock_client.delete_message.return_value = True

    resp = client.delete("/messages/m1")
    assert resp.status_code == HTTP_200_OK

    data = resp.json()
    assert data["success"] is True
    assert "deleted" in data["message"].lower()

    mock_client.delete_message.assert_called_once_with("m1")


def test_mark_as_read(mock_client: Any) -> None:
    """Test POST /messages/{id}/mark-as-read marks message as read."""
    mock_client.mark_as_read.return_value = True

    resp = client.post("/messages/m1/mark-as-read")
    assert resp.status_code == HTTP_200_OK

    data = resp.json()
    assert data["success"] is True
    assert "marked as read" in data["message"].lower()

    mock_client.mark_as_read.assert_called_once_with("m1")


def test_get_message_not_found(mock_client: Any) -> None:
    """Test GET /messages/{id} returns 404 if message not found."""
    mock_client.get_message.side_effect = ValueError("Message not found")

    resp = client.get("/messages/doesnotexist")
    assert resp.status_code == HTTP_404_NOT_FOUND

    data = resp.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_health_check() -> None:
    """Test GET /health always returns healthy status."""
    resp = client.get("/health")
    assert resp.status_code == HTTP_200_OK
    assert resp.json() == {"status": "healthy"}


def test_get_mail_client_dependency(monkeypatch: Any) -> None:
    """Test that get_mail_client returns a client from the factory.

    But patch the factory so we don't hit real GmailClient.
    """
    import mail_client_service.dependencies as deps

    fake_client = MagicMock()
    monkeypatch.setattr(deps, "_client_factory", lambda: fake_client)

    client_obj = deps.get_mail_client()
    assert client_obj is fake_client


def test_dependencies_authentication_failure(monkeypatch: Any) -> None:
    """Test that dependencies raise HTTPException when Gmail client fails."""
    import mail_client_service.dependencies as deps
    from unittest.mock import patch
    from fastapi import HTTPException
    
    # Mock the get_client function to raise exceptions
    with patch('mail_client_service.dependencies.get_client') as mock_get_client:
        # Make it raise RuntimeError
        mock_get_client.side_effect = RuntimeError("No valid credentials found")
        
        # This should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            deps.get_mail_client()
        
        assert exc_info.value.status_code == 503
        assert "Gmail credentials not configured" in exc_info.value.detail
