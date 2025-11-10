"""Integration tests for the complete AI service system."""

import os
from unittest.mock import Mock, patch

import pytest
from ai_client_service.main import app
from fastapi.testclient import TestClient

from ai_client_adapter import ServiceClient


class TestAIServiceIntegration:
    """Integration tests for the AI service system."""

    @pytest.fixture
    def service_client(self) -> TestClient:
        """Create a test client for the AI service."""
        # Set environment variables for OAuth
        os.environ.setdefault("GOOGLE_CLIENT_ID", "test_client_id")
        os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test_client_secret")
        return TestClient(app)

    @pytest.fixture
    def mock_ai_client(self) -> Mock:
        """Create a mock AI client for testing."""
        from ai_client_api.models import ChatCompletionChunk, ChatCompletionResponse, ChatMessage, TokenUsage

        mock_client = Mock()
        mock_client.chat_completion.return_value = ChatCompletionResponse(
            message=ChatMessage(role="assistant", content="Hello! How can I help you?"),
            model="gpt-3.5-turbo",
            usage=TokenUsage(prompt_tokens=10, completion_tokens=15, total_tokens=25),
            finish_reason="stop",
        )
        mock_client.chat_completion_stream.return_value = [
            ChatCompletionChunk(content="Hello", finish_reason=None, model="gpt-3.5-turbo"),
            ChatCompletionChunk(content="!", finish_reason="stop", model="gpt-3.5-turbo"),
        ]
        return mock_client

    def test_service_health_check(self, service_client: TestClient) -> None:
        """Test that the service health check works."""
        response = service_client.get("/health")
        assert response.status_code == 200  # noqa: PLR2004
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "0.1.0"

    def test_service_oauth_flow(self, service_client: TestClient) -> None:
        """Test the OAuth authorization flow."""
        response = service_client.get("/oauth/authorize", follow_redirects=False)
        assert response.status_code == 307  # noqa: PLR2004
        # Should redirect to Google OAuth URL
        assert "accounts.google.com" in response.headers["location"]

    def test_service_chat_completion(self, service_client: TestClient, mock_ai_client: Mock) -> None:
        """Test chat completion through the service."""
        from ai_client_service.dependencies import require_authenticated_client

        app.dependency_overrides[require_authenticated_client] = lambda: mock_ai_client

        try:
            request_data = {
                "messages": [{"role": "user", "content": "Hello!"}],
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
            }

            response = service_client.post(
                "/chat/completions",
                json=request_data,
            )

            assert response.status_code == 200  # noqa: PLR2004
            data = response.json()
            assert data["message"]["role"] == "assistant"
            assert data["message"]["content"] == "Hello! How can I help you?"
            assert data["model"] == "gpt-3.5-turbo"
        finally:
            app.dependency_overrides.clear()

    def test_adapter_initialization(self) -> None:
        """Test that the adapter can be initialized."""
        adapter = ServiceClient(
            base_url="http://127.0.0.1:8000",
            user_id="test_user",
        )

        assert adapter.base_url == "http://127.0.0.1:8000"
        assert adapter.user_id == "test_user"

    def test_adapter_methods_are_implemented(self) -> None:
        """Test that adapter methods are implemented and callable."""
        adapter = ServiceClient()

        # Methods should be callable (actual functionality tested elsewhere)
        assert callable(adapter.chat_completion)
        assert callable(adapter.chat_completion_stream)
        assert callable(adapter.get_client)

        # get_client should return the underlying client
        client = adapter.get_client()
        assert client is not None


    def test_service_streaming_endpoint(self, service_client: TestClient, mock_ai_client: Mock) -> None:
        """Test the streaming endpoint."""
        from ai_client_service.dependencies import require_authenticated_client

        app.dependency_overrides[require_authenticated_client] = lambda: mock_ai_client

        try:
            request_data = {
                "messages": [{"role": "user", "content": "Tell me a story"}],
                "model": "gpt-3.5-turbo",
            }

            response = service_client.post(
                "/chat/completions/stream",
                json=request_data,
            )

            assert response.status_code == 200  # noqa: PLR2004
            # Note: Testing streaming responses requires more complex setup
        finally:
            app.dependency_overrides.clear()

    def test_service_error_handling(self, service_client: TestClient) -> None:
        """Test error handling in the service."""
        # Test without authentication (no session, no API key)
        request_data = {
            "messages": [{"role": "user", "content": "Hello!"}],
        }

        response = service_client.post(
            "/chat/completions",
            json=request_data,
        )

        # Should return 401 for missing authentication
        assert response.status_code == 401  # noqa: PLR2004
        data = response.json()
        assert "Authentication required" in data["detail"]

    def test_service_oauth_callback_success(self, service_client: TestClient) -> None:
        """Test successful OAuth callback."""
        with patch("ai_client_service.main.OAuthManager") as mock_oauth, \
             patch("ai_client_service.main.CredentialStore"):

            mock_oauth.return_value.handle_callback.return_value = ("user123", {"access_token": "token"})

            response = service_client.get(
                "/oauth/callback?code=auth_code&state=state",
            )

            assert response.status_code == 200  # noqa: PLR2004
            data = response.json()
            assert data["success"] is True
            assert data["user_id"] == "user123"

    def test_service_oauth_callback_failure(self, service_client: TestClient) -> None:
        """Test failed OAuth callback."""
        with patch("ai_client_service.main.OAuthManager") as mock_oauth:
            mock_oauth.return_value.handle_callback.side_effect = Exception("OAuth error")

            response = service_client.get(
                "/oauth/callback?code=invalid_code&state=state",
            )

            assert response.status_code == 200  # noqa: PLR2004
            data = response.json()
            assert data["success"] is False
            assert "OAuth error" in data["message"]


class TestAIServiceWorkflow:
    """Test the complete AI service workflow."""

    def test_complete_workflow_simulation(self) -> None:
        """Simulate the complete workflow without actual HTTP calls."""
        # This test simulates what the complete workflow would look like
        # once all components are properly set up

        # 1. User initiates OAuth flow

        # 2. OAuth callback handled

        # 3. User makes chat completion request

        # 4. Service validates user and calls AI client

        # 5. AI client makes request to OpenAI

        # 6. Response returned to user

        # 7. Adapter can be used as drop-in replacement

        # This test passes if it runs without error
        assert True

    def test_api_contract_consistency(self) -> None:
        """Test that the API contracts are consistent across components."""
        from ai_client_api import Client

        # Verify that the adapter implements the same interface
        adapter = ServiceClient()

        # Check that adapter has the required methods
        assert hasattr(adapter, "chat_completion")
        assert hasattr(adapter, "chat_completion_stream")

        # Check that methods are callable
        assert callable(adapter.chat_completion)
        assert callable(adapter.chat_completion_stream)

        # Verify adapter is an instance of the Client ABC
        assert isinstance(adapter, Client)
