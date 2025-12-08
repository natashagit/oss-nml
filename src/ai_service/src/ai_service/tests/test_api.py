"""Tests for AI FastAPI service."""

from unittest.mock import Mock, patch

import pytest
from ai_service.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    """Create a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_ai_client() -> Mock:
    """Create a mock AI client."""
    mock = Mock()
    mock.generate_response.return_value = "Test response from AI"
    return mock


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_check(self, client: TestClient) -> None:
        """Test health check endpoint returns correct status."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "0.1.0"

    def test_health_check_response_model(self, client: TestClient) -> None:
        """Test health check response matches expected schema."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert isinstance(data["status"], str)
        assert isinstance(data["version"], str)


class TestGenerateEndpoint:
    """Tests for the /generate endpoint."""

    def test_generate_conversational_response(
        self, client: TestClient, mock_ai_client: Mock,
    ) -> None:
        """Test generate endpoint with conversational response."""
        with patch("ai_service.main.get_client", return_value=mock_ai_client):
            response = client.post(
                "/generate",
                json={
                    "user_input": "Hello, how are you?",
                    "system_prompt": "You are a helpful assistant.",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["result"] == "Test response from AI"

            # Verify the mock was called correctly
            mock_ai_client.generate_response.assert_called_once_with(
                user_input="Hello, how are you?",
                system_prompt="You are a helpful assistant.",
                response_schema=None,
            )

    def test_generate_structured_response(
        self, client: TestClient, mock_ai_client: Mock,
    ) -> None:
        """Test generate endpoint with structured response."""
        # Mock returns a dict for structured output
        structured_result = {"action": "delete", "message_id": "msg_123"}
        mock_ai_client.generate_response.return_value = structured_result

        response_schema = {
            "name": "email_action",
            "description": "Extract email action",
            "schema": {
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                    "message_id": {"type": "string"},
                },
                "required": ["action", "message_id"],
            },
        }

        with patch("ai_service.main.get_client", return_value=mock_ai_client):
            response = client.post(
                "/generate",
                json={
                    "user_input": "Delete message msg_123",
                    "system_prompt": "You extract email actions.",
                    "response_schema": response_schema,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data["result"], dict)
            assert data["result"]["action"] == "delete"
            assert data["result"]["message_id"] == "msg_123"

            # Verify the mock was called with schema
            mock_ai_client.generate_response.assert_called_once_with(
                user_input="Delete message msg_123",
                system_prompt="You extract email actions.",
                response_schema=response_schema,
            )

    def test_generate_missing_required_fields(self, client: TestClient) -> None:
        """Test generate endpoint with missing required fields."""
        response = client.post(
            "/generate",
            json={
                "user_input": "Hello",
                # Missing system_prompt
            },
        )

        assert response.status_code == 422  # Validation error

    def test_generate_client_initialization_error(
        self, client: TestClient,
    ) -> None:
        """Test generate endpoint handles client initialization errors."""
        with patch(
            "ai_service.main.get_client",
            side_effect=Exception("Failed to initialize client"),
        ):
            response = client.post(
                "/generate",
                json={
                    "user_input": "Test",
                    "system_prompt": "Test prompt",
                },
            )

            assert response.status_code == 500
            assert "Failed to load AI client" in response.json()["detail"]

    def test_generate_response_generation_error(
        self, client: TestClient, mock_ai_client: Mock,
    ) -> None:
        """Test generate endpoint handles response generation errors."""
        mock_ai_client.generate_response.side_effect = Exception("API Error")

        with patch("ai_service.main.get_client", return_value=mock_ai_client):
            response = client.post(
                "/generate",
                json={
                    "user_input": "Test",
                    "system_prompt": "Test prompt",
                },
            )

            assert response.status_code == 500
            assert "Generation failed" in response.json()["detail"]

    def test_generate_with_none_response_schema(
        self, client: TestClient, mock_ai_client: Mock,
    ) -> None:
        """Test generate endpoint explicitly passing None for response_schema."""
        with patch("ai_service.main.get_client", return_value=mock_ai_client):
            response = client.post(
                "/generate",
                json={
                    "user_input": "Hello",
                    "system_prompt": "Test",
                    "response_schema": None,
                },
            )

            assert response.status_code == 200
            mock_ai_client.generate_response.assert_called_once_with(
                user_input="Hello",
                system_prompt="Test",
                response_schema=None,
            )

    def test_generate_response_model_validation(
        self, client: TestClient, mock_ai_client: Mock,
    ) -> None:
        """Test that response follows the GenerateResponse model."""
        with patch("ai_service.main.get_client", return_value=mock_ai_client):
            response = client.post(
                "/generate",
                json={
                    "user_input": "Test",
                    "system_prompt": "Test prompt",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert "result" in data
            # Result can be either string or dict
            assert isinstance(data["result"], (str, dict))
