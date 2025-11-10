"""Tests for AI client adapter."""



from ai_client_adapter.client_impl import ServiceClient


def test_service_client_initialization() -> None:
    """Test ServiceClient initialization."""
    client = ServiceClient(base_url="http://test.com", user_id="test_user")

    assert client.base_url == "http://test.com"
    assert client.user_id == "test_user"


def test_chat_completion_returns_client() -> None:
    """Test that chat_completion can be called (actual testing requires service)."""
    client = ServiceClient()

    # The method exists and is callable
    assert callable(client.chat_completion)
    # Note: Full testing requires a running service, which is tested in integration tests


def test_chat_completion_stream_returns_client() -> None:
    """Test that chat_completion_stream can be called (actual testing requires service)."""
    client = ServiceClient()

    # The method exists and is callable
    assert callable(client.chat_completion_stream)
    # Note: Full testing requires a running service, which is tested in integration tests


def test_get_client_returns_generated_client() -> None:
    """Test that get_client returns the underlying generated client."""
    client = ServiceClient()

    generated_client = client.get_client()
    assert generated_client is not None
    assert generated_client == client.client


# Note: Additional tests for the actual implementation should be added
# once the service client is generated. These tests would mock the
# generated client and test the actual functionality.
