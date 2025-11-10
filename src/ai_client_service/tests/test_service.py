"""Tests for AI client service endpoints."""

import os
from typing import Never
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from ai_client_service.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client."""
    # Set environment variables before creating the app/client
    os.environ.setdefault("GOOGLE_CLIENT_ID", "test_client_id")
    os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test_client_secret")
    return TestClient(app)


@pytest.fixture
def mock_ai_client() -> Mock:
    """Create a mock AI client."""
    from ai_client_api.models import ChatCompletionResponse, ChatMessage, TokenUsage

    mock_client = Mock()
    mock_client.chat_completion.return_value = ChatCompletionResponse(
        message=ChatMessage(role="assistant", content="Hello! How can I help you?"),
        model="gpt-3.5-turbo",
        usage=TokenUsage(prompt_tokens=10, completion_tokens=15, total_tokens=25),
        finish_reason="stop",
    )
    return mock_client


def test_health_check(client: TestClient) -> None:
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200  # noqa: PLR2004
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"


def test_oauth_authorize(client: TestClient) -> None:
    """Test the OAuth authorization endpoint."""
    # Set required environment variables for OAuth
    with patch.dict(os.environ, {"GOOGLE_CLIENT_ID": "test_id", "GOOGLE_CLIENT_SECRET": "test_secret"}):
        response = client.get("/oauth/authorize", follow_redirects=False)
        assert response.status_code == 307  # Redirect  # noqa: PLR2004
        # Should redirect to Google OAuth URL
        assert "accounts.google.com" in response.headers["location"]


def test_oauth_callback_success(client: TestClient) -> None:
    """Test successful OAuth callback."""
    with patch("ai_client_service.main.OAuthManager") as mock_oauth, \
         patch("ai_client_service.main.CredentialStore"):

        mock_oauth.return_value.handle_callback.return_value = ("user123", {"access_token": "token"})

        response = client.get(
            "/oauth/callback?code=auth_code&state=state",
        )

        assert response.status_code == 200  # noqa: PLR2004
        data = response.json()
        assert data["success"] is True
        assert data["user_id"] == "user123"


def test_oauth_callback_failure(client: TestClient) -> None:
    """Test failed OAuth callback."""
    with patch("ai_client_service.main.OAuthManager") as mock_oauth:
        mock_oauth.return_value.handle_callback.side_effect = Exception("OAuth error")

        response = client.get(
            "/oauth/callback?code=invalid_code&state=state",
        )

        assert response.status_code == 200  # noqa: PLR2004
        data = response.json()
        assert data["success"] is False
        assert "OAuth error" in data["message"]


def test_chat_completion_success(client: TestClient, mock_ai_client: Mock) -> None:
    """Test successful chat completion with authentication and API key."""
    # Override the dependency to return our mock client
    from ai_client_service.dependencies import require_authenticated_client
    from ai_client_service.main import app

    app.dependency_overrides[require_authenticated_client] = lambda: mock_ai_client

    try:
        request_data = {
            "messages": [
                {"role": "user", "content": "Hello!"},
            ],
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
        }

        response = client.post(
            "/chat/completions",
            json=request_data,
        )

        assert response.status_code == 200  # noqa: PLR2004
        data = response.json()
        assert data["message"]["role"] == "assistant"
        assert data["message"]["content"] == "Hello! How can I help you?"
        assert data["model"] == "gpt-3.5-turbo"
    finally:
        # Clean up override
        app.dependency_overrides.clear()


def test_chat_completion_stream(client: TestClient, mock_ai_client: Mock) -> None:
    """Test streaming chat completion."""
    from ai_client_api.models import ChatCompletionChunk

    from ai_client_service.dependencies import require_authenticated_client
    from ai_client_service.main import app

    # Mock the streaming response
    mock_ai_client.chat_completion_stream.return_value = [
        ChatCompletionChunk(content="Hello", finish_reason=None, model="gpt-3.5-turbo"),
        ChatCompletionChunk(content="!", finish_reason="stop", model="gpt-3.5-turbo"),
    ]

    app.dependency_overrides[require_authenticated_client] = lambda: mock_ai_client

    try:
        request_data = {
            "messages": [
                {"role": "user", "content": "Hello!"},
            ],
            "model": "gpt-3.5-turbo",
        }

        response = client.post(
            "/chat/completions/stream",
            json=request_data,
        )

        assert response.status_code == 200  # noqa: PLR2004
        # Note: Testing streaming responses requires more complex setup
        # This is a basic test to ensure the endpoint exists and returns 200
    finally:
        app.dependency_overrides.clear()




def test_chat_completion_missing_user_id(client: TestClient) -> None:
    """Test chat completion when user is not authenticated."""
    from fastapi import HTTPException

    from ai_client_service.dependencies import require_authenticated_client
    from ai_client_service.main import app

    def mock_auth_error() -> Never:
        # Mimic the behavior of require_authenticated_client when API key is missing
        raise HTTPException(
            status_code=400,
            detail="OpenAI API key not set. Please set your API key using POST /api-keys",
        )

    app.dependency_overrides[require_authenticated_client] = mock_auth_error

    try:
        request_data = {
            "messages": [{"role": "user", "content": "Hello!"}],
        }

        response = client.post(
            "/chat/completions",
            json=request_data,
        )

        assert response.status_code == 400  # noqa: PLR2004
        data = response.json()
        assert "OpenAI API key not set" in data["detail"]
    finally:
        app.dependency_overrides.clear()
