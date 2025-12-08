"""Tests for OpenAI client implementation."""

from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest

from openai_impl.openai_impl import OpenAIClient


class TestOpenAIClient:
    """Test suite for OpenAIClient."""

    def test_init_with_api_key(self) -> None:
        """Test initialization with explicit API key."""
        with patch("openai_impl.openai_impl.OpenAI") as mock_openai:
            client = OpenAIClient(api_key="test-key-123")
            assert client.model == "gpt-4o-mini"
            mock_openai.assert_called_once_with(api_key="test-key-123")

    def test_init_with_env_var(self) -> None:
        """Test initialization with API key from environment variable."""
        with (
            patch("openai_impl.openai_impl.OpenAI") as mock_openai,
            patch.dict("os.environ", {"OPENAI_API_KEY": "env-key-456"}),
        ):
            client = OpenAIClient()
            assert client.model == "gpt-4o-mini"
            mock_openai.assert_called_once_with(api_key="env-key-456")

    def test_init_without_api_key_raises_error(self) -> None:
        """Test that initialization without API key raises RuntimeError."""
        with (
            patch.dict("os.environ", {}, clear=True),
            pytest.raises(RuntimeError, match="No OpenAI API key found"),
        ):
            OpenAIClient()

    def test_init_with_custom_model(self) -> None:
        """Test initialization with custom model."""
        with patch("openai_impl.openai_impl.OpenAI"):
            client = OpenAIClient(api_key="test-key", model="gpt-4")
            assert client.model == "gpt-4"

    def test_generate_response_conversational(
        self, mock_openai_response: dict[str, Any],
    ) -> None:
        """Test generate_response returns text content for conversational mode."""
        with patch("openai_impl.openai_impl.OpenAI") as mock_openai_class:
            # Setup mock
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client

            # Create mock response object
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = (
                "This is a test response from the AI assistant."
            )
            mock_client.chat.completions.create.return_value = mock_response

            # Test
            client = OpenAIClient(api_key="test-key")
            result = client.generate_response(
                user_input="Hello, how are you?",
                system_prompt="You are a helpful assistant.",
            )

            # Verify
            assert result == "This is a test response from the AI assistant."
            mock_client.chat.completions.create.assert_called_once()
            call_kwargs = mock_client.chat.completions.create.call_args[1]
            assert call_kwargs["model"] == "gpt-4o-mini"
            assert len(call_kwargs["messages"]) == 2
            assert call_kwargs["messages"][0]["role"] == "system"
            assert call_kwargs["messages"][1]["role"] == "user"

    def test_generate_response_structured(
        self, mock_openai_structured_response: dict[str, Any],
    ) -> None:
        """Test generate_response returns structured dict when schema provided."""
        with patch("openai_impl.openai_impl.OpenAI") as mock_openai_class:
            # Setup mock
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client

            # Create mock response object
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = (
                '{"action": "delete", "message_id": "msg_123"}'
            )
            mock_client.chat.completions.create.return_value = mock_response

            # Test
            client = OpenAIClient(api_key="test-key")
            response_schema = {
                "name": "email_action",
                "description": "Extract email action intent",
                "schema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string"},
                        "message_id": {"type": "string"},
                    },
                    "required": ["action", "message_id"],
                },
            }

            result = client.generate_response(
                user_input="Delete message msg_123",
                system_prompt="You extract email actions.",
                response_schema=response_schema,
            )

            # Verify
            assert isinstance(result, dict)
            assert result["action"] == "delete"
            assert result["message_id"] == "msg_123"

            # Verify API call
            mock_client.chat.completions.create.assert_called_once()
            call_kwargs = mock_client.chat.completions.create.call_args[1]
            assert "response_format" in call_kwargs
            assert call_kwargs["response_format"]["type"] == "json_schema"

    def test_generate_response_empty_content(self) -> None:
        """Test generate_response handles empty content gracefully."""
        with patch("openai_impl.openai_impl.OpenAI") as mock_openai_class:
            # Setup mock with empty content
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client

            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = None
            mock_client.chat.completions.create.return_value = mock_response

            # Test conversational mode
            client = OpenAIClient(api_key="test-key")
            result = client.generate_response(
                user_input="Test", system_prompt="Test prompt",
            )
            assert result == ""

    def test_generate_response_structured_empty_content(self) -> None:
        """Test generate_response returns empty dict when structured content is None."""
        with patch("openai_impl.openai_impl.OpenAI") as mock_openai_class:
            # Setup mock with empty content
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client

            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = None
            mock_client.chat.completions.create.return_value = mock_response

            # Test structured mode
            client = OpenAIClient(api_key="test-key")
            result = client.generate_response(
                user_input="Test",
                system_prompt="Test prompt",
                response_schema={"type": "object"},
            )
            assert result == {}

    def test_generate_response_api_error(self) -> None:
        """Test generate_response raises RuntimeError on API failure."""
        with patch("openai_impl.openai_impl.OpenAI") as mock_openai_class:
            # Setup mock to raise exception
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("API Error")

            # Test
            client = OpenAIClient(api_key="test-key")
            with pytest.raises(RuntimeError, match="Failed to generate response"):
                client.generate_response(
                    user_input="Test", system_prompt="Test prompt",
                )

    def test_schema_strict_mode_enforcement(self) -> None:
        """Test that strict mode is enforced for structured outputs."""
        with patch("openai_impl.openai_impl.OpenAI") as mock_openai_class:
            # Setup mock
            mock_client = MagicMock()
            mock_openai_class.return_value = mock_client

            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = '{"test": "value"}'
            mock_client.chat.completions.create.return_value = mock_response

            # Test with schema without additionalProperties
            client = OpenAIClient(api_key="test-key")
            response_schema = {
                "name": "test_schema",
                "schema": {
                    "type": "object",
                    "properties": {"test": {"type": "string"}},
                },
            }

            client.generate_response(
                user_input="Test",
                system_prompt="Test",
                response_schema=response_schema,
            )

            # Verify strict mode is set
            call_kwargs = mock_client.chat.completions.create.call_args[1]
            json_schema = call_kwargs["response_format"]["json_schema"]
            assert json_schema["strict"] is True
            assert json_schema["schema"]["additionalProperties"] is False
