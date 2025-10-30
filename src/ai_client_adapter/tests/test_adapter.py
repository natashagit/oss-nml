"""Tests for AI client adapter."""

import pytest

from ai_client_adapter.client_impl import ServiceClient


def test_service_client_initialization() -> None:
    """Test ServiceClient initialization."""
    client = ServiceClient(base_url="http://test.com", user_id="test_user")

    assert client.base_url == "http://test.com"
    assert client.user_id == "test_user"


def test_chat_completion_not_implemented() -> None:
    """Test that chat_completion raises NotImplementedError before client generation."""
    client = ServiceClient()

    with pytest.raises(NotImplementedError, match="Service client not yet generated"):
        client.chat_completion([{"role": "user", "content": "Hello"}])


def test_chat_completion_stream_not_implemented() -> None:
    """Test that chat_completion_stream raises NotImplementedError before client generation."""
    client = ServiceClient()

    with pytest.raises(NotImplementedError, match="Service client not yet generated"):
        list(client.chat_completion_stream([{"role": "user", "content": "Hello"}]))


def test_get_client_not_implemented() -> None:
    """Test that get_client raises NotImplementedError before client generation."""
    client = ServiceClient()

    with pytest.raises(NotImplementedError, match="Service client not yet generated"):
        client.get_client()


# TODO: Add tests for the actual implementation once the service client is generated
# These tests would mock the generated client and test the actual functionality
