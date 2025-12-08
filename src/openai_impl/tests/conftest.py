"""Pytest fixtures for OpenAI implementation tests."""

from typing import Any

import pytest


@pytest.fixture
def mock_openai_response() -> dict[str, Any]:
    """Mock OpenAI API response for chat completion.

    Returns a realistic OpenAI chat completion response structure
    that mimics the actual API response format.
    """
    return {
        "id": "chatcmpl-test123",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gpt-4o-mini",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This is a test response from the AI assistant.",
                },
                "finish_reason": "stop",
            },
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30,
        },
    }


@pytest.fixture
def mock_openai_structured_response() -> dict[str, Any]:
    """Mock OpenAI API response for structured output.

    Returns a chat completion response with JSON structured content.
    """
    return {
        "id": "chatcmpl-test456",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gpt-4o-mini",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": '{"action": "delete", "message_id": "msg_123"}',
                },
                "finish_reason": "stop",
            },
        ],
        "usage": {
            "prompt_tokens": 15,
            "completion_tokens": 10,
            "total_tokens": 25,
        },
    }
