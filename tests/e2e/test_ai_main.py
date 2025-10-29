"""End-to-end tests for the AI main.py module."""

import pytest
from unittest.mock import Mock, patch

from main import main


@patch("openai_client_impl.register")
@patch("ai_client_api.get_client")
def test_main_with_successful_client(mock_get_client, mock_register):
    """Test main function with a successful client."""
    # Mock the AI client
    mock_client = Mock()
    mock_client.chat_completion.return_value = {
        "message": {"content": "Why don't scientists trust atoms? Because they make up everything!"},
        "model": "gpt-3.5-turbo",
        "usage": {"total_tokens": 20},
        "finish_reason": "stop"
    }
    mock_client.chat_completion_stream.return_value = [
        {"content": "Once upon a time, there was a robot", "finish_reason": None, "model": "gpt-3.5-turbo"},
        {"content": " who loved to dance.", "finish_reason": "stop", "model": "gpt-3.5-turbo"}
    ]
    mock_get_client.return_value = mock_client
    
    # This should not raise any exceptions
    main()
    
    # Verify that register was called
    mock_register.assert_called_once()
    
    # Verify that the client methods were called
    assert mock_client.chat_completion.call_count == 2  # Once for basic, once for advanced
    assert mock_client.chat_completion_stream.call_count == 1


@patch("openai_client_impl.register")
@patch("ai_client_api.get_client")
def test_main_with_client_initialization_failure(mock_get_client, mock_register):
    """Test main function when client initialization fails."""
    mock_get_client.side_effect = Exception("No credentials found")
    
    # This should not raise any exceptions, just log and return
    main()
    
    # Verify that register was called
    mock_register.assert_called_once()
    
    # Verify that get_client was called
    mock_get_client.assert_called_once_with("demo_user")


@patch("openai_client_impl.register")
@patch("ai_client_api.get_client")
def test_main_with_chat_completion_failure(mock_get_client, mock_register):
    """Test main function when chat completion fails."""
    mock_client = Mock()
    mock_client.chat_completion.side_effect = Exception("API error")
    mock_client.chat_completion_stream.return_value = []
    mock_get_client.return_value = mock_client
    
    # This should not raise any exceptions, just log errors
    main()
    
    # Verify that register was called
    mock_register.assert_called_once()
    
    # Verify that the methods were called despite errors
    assert mock_client.chat_completion.call_count == 2
    assert mock_client.chat_completion_stream.call_count == 1


def test_main_imports():
    """Test that main.py can be imported without errors."""
    import main
    assert hasattr(main, 'main')
    assert callable(main.main)
