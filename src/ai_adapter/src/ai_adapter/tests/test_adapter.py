"""Tests for AI service adapter."""

from typing import Any
from unittest.mock import Mock, patch

import pytest

from ai_adapter.client_impl import ServiceClient


class TestServiceClient:
    """Test suite for ServiceClient adapter."""

    def test_init_default_base_url(self) -> None:
        """Test initialization with default base URL."""
        with patch("ai_adapter.client_impl.GeneratedClient") as mock_client_class:
            ServiceClient()
            mock_client_class.assert_called_once_with(base_url="http://127.0.0.1:8000")

    def test_init_custom_base_url(self) -> None:
        """Test initialization with custom base URL."""
        with patch("ai_adapter.client_impl.GeneratedClient") as mock_client_class:
            ServiceClient(base_url="http://localhost:9000")
            mock_client_class.assert_called_once_with(base_url="http://localhost:9000")

    def test_generate_response_conversational(self) -> None:
        """Test generate_response returns text for conversational mode."""
        with patch("ai_adapter.client_impl.GeneratedClient") as mock_client_class:
            # Setup mock
            mock_client_instance = Mock()
            mock_client_class.return_value = mock_client_instance

            # Mock the response
            mock_response = Mock()
            mock_response.result = "This is a conversational response"

            with patch(
                "ai_adapter.client_impl.generate_generate_post.sync",
                return_value=mock_response,
            ) as mock_generate:
                client = ServiceClient()
                result = client.generate_response(
                    user_input="Hello, how are you?",
                    system_prompt="You are a helpful assistant.",
                )

                # Verify result
                assert result == "This is a conversational response"

                # Verify the API call
                mock_generate.assert_called_once()
                call_args = mock_generate.call_args
                assert call_args[1]["client"] == mock_client_instance

                # Verify the request body
                body = call_args[1]["body"]
                assert body.user_input == "Hello, how are you?"
                assert body.system_prompt == "You are a helpful assistant."
                assert body.response_schema is None

    def test_generate_response_structured(self) -> None:
        """Test generate_response returns dict for structured mode."""
        with patch("ai_adapter.client_impl.GeneratedClient") as mock_client_class:
            # Setup mock
            mock_client_instance = Mock()
            mock_client_class.return_value = mock_client_instance

            # Mock the response with structured data
            mock_response = Mock()
            mock_response.result = {"action": "delete", "message_id": "msg_123"}

            response_schema = {
                "name": "email_action",
                "description": "Extract email action",
                "schema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string"},
                        "message_id": {"type": "string"},
                    },
                },
            }

            with patch(
                "ai_adapter.client_impl.generate_generate_post.sync",
                return_value=mock_response,
            ) as mock_generate:
                client = ServiceClient()
                result = client.generate_response(
                    user_input="Delete message msg_123",
                    system_prompt="You extract email actions.",
                    response_schema=response_schema,
                )

                # Verify result
                assert isinstance(result, dict)
                assert result["action"] == "delete"
                assert result["message_id"] == "msg_123"

                # Verify the request body includes schema
                body = mock_generate.call_args[1]["body"]
                assert body.response_schema == response_schema

    def test_generate_response_none_response_raises_error(self) -> None:
        """Test generate_response raises RuntimeError when response is None."""
        with patch("ai_adapter.client_impl.GeneratedClient"):
            with patch(
                "ai_adapter.client_impl.generate_generate_post.sync",
                return_value=None,
            ):
                client = ServiceClient()
                with pytest.raises(
                    RuntimeError, match="No response returned from AI service"
                ):
                    client.generate_response(
                        user_input="Test",
                        system_prompt="Test prompt",
                    )

    def test_generate_response_with_none_schema(self) -> None:
        """Test generate_response with explicitly None response_schema."""
        with patch("ai_adapter.client_impl.GeneratedClient") as mock_client_class:
            mock_client_instance = Mock()
            mock_client_class.return_value = mock_client_instance

            mock_response = Mock()
            mock_response.result = "Response text"

            with patch(
                "ai_adapter.client_impl.generate_generate_post.sync",
                return_value=mock_response,
            ) as mock_generate:
                client = ServiceClient()
                result = client.generate_response(
                    user_input="Test",
                    system_prompt="Test prompt",
                    response_schema=None,
                )

                assert result == "Response text"

                # Verify None was passed
                body = mock_generate.call_args[1]["body"]
                assert body.response_schema is None

    def test_generate_response_request_body_construction(self) -> None:
        """Test that GenerateRequest body is constructed correctly."""
        with patch("ai_adapter.client_impl.GeneratedClient") as mock_client_class:
            mock_client_instance = Mock()
            mock_client_class.return_value = mock_client_instance

            mock_response = Mock()
            mock_response.result = "Test"

            with patch(
                "ai_adapter.client_impl.generate_generate_post.sync",
                return_value=mock_response,
            ) as mock_generate:
                client = ServiceClient()

                test_schema: dict[str, Any] = {"type": "object"}
                client.generate_response(
                    user_input="Test input",
                    system_prompt="Test system",
                    response_schema=test_schema,
                )

                # Verify GenerateRequest was created with correct fields
                body = mock_generate.call_args[1]["body"]
                assert hasattr(body, "user_input")
                assert hasattr(body, "system_prompt")
                assert hasattr(body, "response_schema")
                assert body.user_input == "Test input"
                assert body.system_prompt == "Test system"
                assert body.response_schema == test_schema

    def test_multiple_calls_use_same_client(self) -> None:
        """Test that multiple calls reuse the same underlying client."""
        with patch("ai_adapter.client_impl.GeneratedClient") as mock_client_class:
            mock_client_instance = Mock()
            mock_client_class.return_value = mock_client_instance

            mock_response = Mock()
            mock_response.result = "Response"

            with patch(
                "ai_adapter.client_impl.generate_generate_post.sync",
                return_value=mock_response,
            ):
                client = ServiceClient()

                # Make multiple calls
                client.generate_response("Test 1", "Prompt 1")
                client.generate_response("Test 2", "Prompt 2")

                # Client should only be instantiated once
                assert mock_client_class.call_count == 1
