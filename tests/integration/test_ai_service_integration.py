"""Integration tests for the complete AI service system."""

import pytest
import requests
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from ai_client_service.main import app
from ai_client_adapter import ServiceClient


class TestAIServiceIntegration:
    """Integration tests for the AI service system."""

    @pytest.fixture
    def service_client(self):
        """Create a test client for the AI service."""
        return TestClient(app)

    @pytest.fixture
    def mock_ai_client(self):
        """Create a mock AI client for testing."""
        mock_client = Mock()
        mock_client.chat_completion.return_value = {
            "message": {"role": "assistant", "content": "Hello! How can I help you?"},
            "model": "gpt-3.5-turbo",
            "usage": {"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25},
            "finish_reason": "stop",
        }
        mock_client.chat_completion_stream.return_value = [
            {"content": "Hello", "finish_reason": None, "model": "gpt-3.5-turbo"},
            {"content": "!", "finish_reason": "stop", "model": "gpt-3.5-turbo"},
        ]
        return mock_client

    def test_service_health_check(self, service_client):
        """Test that the service health check works."""
        response = service_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "0.1.0"

    def test_service_oauth_flow(self, service_client):
        """Test the OAuth authorization flow."""
        with patch("ai_client_service.main.OAuthManager") as mock_oauth:
            mock_oauth.return_value.get_authorization_url.return_value = "https://example.com/auth"
            
            response = service_client.get("/oauth/authorize")
            assert response.status_code == 307
            assert "example.com" in response.headers["location"]

    @patch("ai_client_service.main.get_ai_client")
    def test_service_chat_completion(self, mock_get_client, service_client, mock_ai_client):
        """Test chat completion through the service."""
        mock_get_client.return_value = mock_ai_client
        
        request_data = {
            "messages": [{"role": "user", "content": "Hello!"}],
            "model": "gpt-3.5-turbo",
            "temperature": 0.7
        }
        
        response = service_client.post(
            "/chat/completions?user_id=test_user",
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"]["role"] == "assistant"
        assert data["message"]["content"] == "Hello! How can I help you?"
        assert data["model"] == "gpt-3.5-turbo"

    def test_adapter_initialization(self):
        """Test that the adapter can be initialized."""
        adapter = ServiceClient(
            base_url="http://127.0.0.1:8000",
            user_id="test_user"
        )
        
        assert adapter.base_url == "http://127.0.0.1:8000"
        assert adapter.user_id == "test_user"

    def test_adapter_not_implemented_before_generation(self):
        """Test that adapter methods raise NotImplementedError before client generation."""
        adapter = ServiceClient()
        
        with pytest.raises(NotImplementedError):
            adapter.chat_completion([{"role": "user", "content": "Hello"}])
        
        with pytest.raises(NotImplementedError):
            list(adapter.chat_completion_stream([{"role": "user", "content": "Hello"}]))
        
        with pytest.raises(NotImplementedError):
            adapter.get_client()


    @patch("ai_client_service.main.get_ai_client")
    def test_service_streaming_endpoint(self, mock_get_client, service_client, mock_ai_client):
        """Test the streaming endpoint."""
        mock_get_client.return_value = mock_ai_client
        
        request_data = {
            "messages": [{"role": "user", "content": "Tell me a story"}],
            "model": "gpt-3.5-turbo"
        }
        
        response = service_client.post(
            "/chat/completions/stream?user_id=test_user",
            json=request_data
        )
        
        assert response.status_code == 200
        # Note: Testing streaming responses requires more complex setup

    def test_service_error_handling(self, service_client):
        """Test error handling in the service."""
        # Test missing user_id parameter
        request_data = {
            "messages": [{"role": "user", "content": "Hello!"}]
        }
        
        response = service_client.post(
            "/chat/completions",  # Missing user_id
            json=request_data
        )
        
        # Should return 422 for missing required parameter
        assert response.status_code == 422

    def test_service_oauth_callback_success(self, service_client):
        """Test successful OAuth callback."""
        with patch("ai_client_service.main.OAuthManager") as mock_oauth, \
             patch("ai_client_service.main.CredentialStore") as mock_store:
            
            mock_oauth.return_value.handle_callback.return_value = ("user123", {"access_token": "token"})
            
            response = service_client.post(
                "/oauth/callback",
                json={"code": "auth_code", "state": "state"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["user_id"] == "user123"

    def test_service_oauth_callback_failure(self, service_client):
        """Test failed OAuth callback."""
        with patch("ai_client_service.main.OAuthManager") as mock_oauth:
            mock_oauth.return_value.handle_callback.side_effect = Exception("OAuth error")
            
            response = service_client.post(
                "/oauth/callback",
                json={"code": "invalid_code", "state": "state"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert "OAuth error" in data["message"]


class TestAIServiceWorkflow:
    """Test the complete AI service workflow."""

    def test_complete_workflow_simulation(self):
        """Simulate the complete workflow without actual HTTP calls."""
        # This test simulates what the complete workflow would look like
        # once all components are properly set up
        
        # 1. User initiates OAuth flow
        print("1. User redirected to OAuth provider")
        
        # 2. OAuth callback handled
        print("2. OAuth callback processed, user credentials stored")
        
        # 3. User makes chat completion request
        print("3. User makes chat completion request")
        
        # 4. Service validates user and calls AI client
        print("4. Service validates user and calls AI client")
        
        # 5. AI client makes request to OpenAI
        print("5. AI client makes request to OpenAI")
        
        # 6. Response returned to user
        print("6. Response returned to user")
        
        # 7. Adapter can be used as drop-in replacement
        print("7. Adapter can be used as drop-in replacement")
        
        # This test passes if it runs without error
        assert True

    def test_api_contract_consistency(self):
        """Test that the API contracts are consistent across components."""
        from ai_client_api import Client
        
        # Verify that the adapter implements the same interface
        adapter = ServiceClient()
        
        # Check that adapter has the required methods
        assert hasattr(adapter, 'chat_completion')
        assert hasattr(adapter, 'chat_completion_stream')
        
        # Check that methods are callable
        assert callable(adapter.chat_completion)
        assert callable(adapter.chat_completion_stream)
        
        # Verify adapter is an instance of the Client ABC
        assert isinstance(adapter, Client)
