"""Tests for AI client service endpoints."""

from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from ai_client_service.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_ai_client():
    """Create a mock AI client."""
    mock_client = Mock()
    mock_client.chat_completion.return_value = {
        "message": {"role": "assistant", "content": "Hello! How can I help you?"},
        "model": "gpt-3.5-turbo",
        "usage": {"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25},
        "finish_reason": "stop",
    }
    return mock_client


def test_health_check(client) -> None:
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"


def test_oauth_authorize(client) -> None:
    """Test the OAuth authorization endpoint."""
    with patch("ai_client_service.main.OAuthManager") as mock_oauth:
        mock_oauth.return_value.get_authorization_url.return_value = "https://example.com/auth"

        response = client.get("/oauth/authorize")
        assert response.status_code == 307  # Redirect
        assert "example.com" in response.headers["location"]


def test_oauth_callback_success(client) -> None:
    """Test successful OAuth callback."""
    with (
        patch("ai_client_service.main.OAuthManager") as mock_oauth,
        patch("ai_client_service.main.CredentialStore"),
    ):
        mock_oauth.return_value.handle_callback.return_value = (
            "user123",
            {"access_token": "token"},
        )

        response = client.post(
            "/oauth/callback",
            json={"code": "auth_code", "state": "state"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["user_id"] == "user123"


def test_oauth_callback_failure(client) -> None:
    """Test failed OAuth callback."""
    with patch("ai_client_service.main.OAuthManager") as mock_oauth:
        mock_oauth.return_value.handle_callback.side_effect = Exception("OAuth error")

        response = client.post(
            "/oauth/callback",
            json={"code": "invalid_code", "state": "state"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "OAuth error" in data["message"]


@patch("ai_client_service.main.get_ai_client")
def test_chat_completion_success(mock_get_client, client, mock_ai_client) -> None:
    """Test successful chat completion."""
    mock_get_client.return_value = mock_ai_client

    request_data = {
        "messages": [
            {"role": "user", "content": "Hello!"},
        ],
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
    }

    response = client.post(
        "/chat/completions?user_id=test_user",
        json=request_data,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"]["role"] == "assistant"
    assert data["message"]["content"] == "Hello! How can I help you?"
    assert data["model"] == "gpt-3.5-turbo"


@patch("ai_client_service.main.get_ai_client")
def test_chat_completion_stream(mock_get_client, client, mock_ai_client) -> None:
    """Test streaming chat completion."""
    mock_get_client.return_value = mock_ai_client

    # Mock the streaming response
    mock_ai_client.chat_completion_stream.return_value = [
        {"content": "Hello", "finish_reason": None, "model": "gpt-3.5-turbo"},
        {"content": "!", "finish_reason": "stop", "model": "gpt-3.5-turbo"},
    ]

    request_data = {
        "messages": [
            {"role": "user", "content": "Hello!"},
        ],
        "model": "gpt-3.5-turbo",
    }

    response = client.post(
        "/chat/completions/stream?user_id=test_user",
        json=request_data,
    )

    assert response.status_code == 200
    # Note: Testing streaming responses requires more complex setup
    # This is a basic test to ensure the endpoint exists


@patch("ai_client_service.main.get_ai_client")
def test_chat_completion_missing_user_id(mock_get_client, client) -> None:
    """Test chat completion without user_id parameter."""
    mock_get_client.side_effect = ValueError("No OpenAI API key found for user test_user")

    request_data = {
        "messages": [{"role": "user", "content": "Hello!"}],
    }

    response = client.post(
        "/chat/completions?user_id=test_user",
        json=request_data,
    )

    assert response.status_code == 500
    data = response.json()
    assert "Failed to create chat completion" in data["detail"]
