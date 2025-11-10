"""Tests for OpenAI client implementation."""

# ruff: noqa: ANN001, ANN201, PLR2004, SIM117

import os
from unittest.mock import Mock, patch

import pytest
from ai_client_api.models import ChatCompletionChunk, ChatCompletionResponse, ChatMessage

from openai_client_impl.openai_impl import OpenAIClient, get_client_impl, register


@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client."""
    with patch("openai_client_impl.openai_impl.OpenAI") as mock:
        yield mock


@pytest.fixture
def mock_credential_store():
    """Create a mock CredentialStore."""
    with patch("openai_client_impl.openai_impl.CredentialStore") as mock:
        store = Mock()
        mock.return_value = store
        yield store


class TestOpenAIClientInit:
    """Test OpenAIClient initialization."""

    def test_init_with_api_key_parameter(self, mock_openai_client) -> None:
        """Test initialization with explicit API key parameter."""
        client = OpenAIClient(user_id="test_user", openai_api_key="test-key")

        assert client.user_id == "test_user"
        mock_openai_client.assert_called_once_with(api_key="test-key")

    def test_init_with_env_variable(self, mock_openai_client) -> None:
        """Test initialization with environment variable."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env-test-key"}):
            client = OpenAIClient(user_id="test_user")

            assert client.user_id == "test_user"
            mock_openai_client.assert_called_once_with(api_key="env-test-key")

    def test_init_with_database(self, mock_openai_client, mock_credential_store) -> None:
        """Test initialization with database credentials."""
        mock_credential_store.get_openai_api_key.return_value = "db-test-key"

        with patch.dict(os.environ, {}, clear=True):
            client = OpenAIClient(user_id="test_user")

            assert client.user_id == "test_user"
            mock_credential_store.get_openai_api_key.assert_called_once_with("test_user")
            mock_openai_client.assert_called_once_with(api_key="db-test-key")

    def test_init_with_project_and_org(self, mock_openai_client) -> None:
        """Test initialization with project and organization."""
        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "test-key",
                "OPENAI_PROJECT": "test-project",
                "OPENAI_ORG": "test-org",
            },
        ):
            client = OpenAIClient(user_id="test_user")

            assert client.user_id == "test_user"
            mock_openai_client.assert_called_once_with(
                api_key="test-key",
                project="test-project",
                organization="test-org",
            )

    def test_init_no_api_key_raises_error(self, mock_credential_store) -> None:
        """Test that initialization fails when no API key is found."""
        mock_credential_store.get_openai_api_key.return_value = None

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="No OpenAI API key found"):
                OpenAIClient(user_id="test_user")

    def test_init_strips_whitespace_from_api_key(self, mock_openai_client) -> None:
        """Test that API keys are stripped of whitespace."""
        OpenAIClient(user_id="test_user", openai_api_key="  test-key  ")

        mock_openai_client.assert_called_once_with(api_key="test-key")


class TestChatCompletion:
    """Test chat completion functionality."""

    def test_chat_completion_success(self, mock_openai_client) -> None:
        """Test successful chat completion."""
        # Setup mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock(role="assistant", content="Hello!")
        mock_response.choices[0].finish_reason = "stop"
        mock_response.model = "gpt-3.5-turbo"
        mock_response.usage = Mock(prompt_tokens=10, completion_tokens=5, total_tokens=15)

        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai_client.return_value = mock_client_instance

        # Create client and make request
        client = OpenAIClient(user_id="test_user", openai_api_key="test-key")
        messages = [ChatMessage(role="user", content="Hi")]
        result = client.chat_completion(messages)

        # Verify
        assert isinstance(result, ChatCompletionResponse)
        assert result.message.role == "assistant"
        assert result.message.content == "Hello!"
        assert result.model == "gpt-3.5-turbo"
        assert result.usage.total_tokens == 15
        assert result.finish_reason == "stop"

    def test_chat_completion_with_params(self, mock_openai_client) -> None:
        """Test chat completion with custom parameters."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock(role="assistant", content="Response")
        mock_response.choices[0].finish_reason = "length"
        mock_response.model = "gpt-4"
        mock_response.usage = Mock(prompt_tokens=20, completion_tokens=10, total_tokens=30)

        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai_client.return_value = mock_client_instance

        client = OpenAIClient(user_id="test_user", openai_api_key="test-key")
        messages = [ChatMessage(role="user", content="Test")]
        result = client.chat_completion(
            messages, model="gpt-4", temperature=0.5, max_tokens=100,
        )

        # Verify parameters were passed
        mock_client_instance.chat.completions.create.assert_called_once_with(
            model="gpt-4",
            messages=[{"role": "user", "content": "Test"}],
            temperature=0.5,
            max_tokens=100,
        )
        assert result.message.content == "Response"

    def test_chat_completion_api_error(self, mock_openai_client) -> None:
        """Test chat completion when API returns an error."""
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.side_effect = Exception("API Error")
        mock_openai_client.return_value = mock_client_instance

        client = OpenAIClient(user_id="test_user", openai_api_key="test-key")
        messages = [ChatMessage(role="user", content="Test")]

        with pytest.raises(Exception, match="API Error"):
            client.chat_completion(messages)

    def test_chat_completion_no_usage(self, mock_openai_client) -> None:
        """Test chat completion when usage data is missing."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock(role="assistant", content="Hello!")
        mock_response.choices[0].finish_reason = "stop"
        mock_response.model = "gpt-3.5-turbo"
        mock_response.usage = None  # No usage data

        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai_client.return_value = mock_client_instance

        client = OpenAIClient(user_id="test_user", openai_api_key="test-key")
        messages = [ChatMessage(role="user", content="Test")]
        result = client.chat_completion(messages)

        # Should default to 0 for all token counts
        assert result.usage.prompt_tokens == 0
        assert result.usage.completion_tokens == 0
        assert result.usage.total_tokens == 0


class TestChatCompletionStream:
    """Test streaming chat completion functionality."""

    def test_chat_completion_stream_success(self, mock_openai_client) -> None:
        """Test successful streaming chat completion."""
        # Setup mock stream
        mock_chunk1 = Mock()
        mock_chunk1.choices = [Mock()]
        mock_chunk1.choices[0].delta = Mock(content="Hello")
        mock_chunk1.choices[0].finish_reason = None
        mock_chunk1.model = "gpt-3.5-turbo"

        mock_chunk2 = Mock()
        mock_chunk2.choices = [Mock()]
        mock_chunk2.choices[0].delta = Mock(content=" world!")
        mock_chunk2.choices[0].finish_reason = "stop"
        mock_chunk2.model = "gpt-3.5-turbo"

        mock_stream = [mock_chunk1, mock_chunk2]

        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_stream
        mock_openai_client.return_value = mock_client_instance

        # Create client and stream
        client = OpenAIClient(user_id="test_user", openai_api_key="test-key")
        messages = [ChatMessage(role="user", content="Hi")]
        chunks = list(client.chat_completion_stream(messages))

        # Verify
        assert len(chunks) == 2
        assert isinstance(chunks[0], ChatCompletionChunk)
        assert chunks[0].content == "Hello"
        assert chunks[0].finish_reason is None
        assert chunks[1].content == " world!"
        assert chunks[1].finish_reason == "stop"

    def test_chat_completion_stream_empty_choices(self, mock_openai_client) -> None:
        """Test streaming with empty choices (should be skipped)."""
        mock_chunk = Mock()
        mock_chunk.choices = []  # Empty choices

        mock_stream = [mock_chunk]

        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_stream
        mock_openai_client.return_value = mock_client_instance

        client = OpenAIClient(user_id="test_user", openai_api_key="test-key")
        messages = [ChatMessage(role="user", content="Test")]
        chunks = list(client.chat_completion_stream(messages))

        # Should skip empty chunks
        assert len(chunks) == 0

    def test_chat_completion_stream_api_error(self, mock_openai_client) -> None:
        """Test streaming when API returns an error."""
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.side_effect = Exception("Stream Error")
        mock_openai_client.return_value = mock_client_instance

        client = OpenAIClient(user_id="test_user", openai_api_key="test-key")
        messages = [ChatMessage(role="user", content="Test")]

        with pytest.raises(Exception, match="Stream Error"):
            list(client.chat_completion_stream(messages))


class TestGetClientImpl:
    """Test get_client_impl function."""

    def test_get_client_impl_returns_client(self, mock_openai_client) -> None:
        """Test that get_client_impl returns an OpenAIClient instance."""
        client = get_client_impl(user_id="test_user", openai_api_key="test-key")

        assert isinstance(client, OpenAIClient)
        assert client.user_id == "test_user"


class TestRegister:
    """Test register function."""

    def test_register_sets_get_client(self, mock_openai_client) -> None:
        """Test that register sets up the get_client function."""
        import ai_client_api

        # Store original
        original_get_client = getattr(ai_client_api, "get_client", None)

        try:
            register(openai_api_key="test-key")

            # Verify get_client was set
            assert hasattr(ai_client_api, "get_client")
            assert callable(ai_client_api.get_client)

            # Test calling it
            client = ai_client_api.get_client("test_user")
            assert isinstance(client, OpenAIClient)
            assert client.user_id == "test_user"

        finally:
            # Restore original
            if original_get_client:
                ai_client_api.get_client = original_get_client
