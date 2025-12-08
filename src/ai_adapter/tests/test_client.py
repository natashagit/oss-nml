"""Unit tests for the AI adapter."""

from unittest.mock import patch

import pytest
from ai_adapter.client_impl import ServiceClient
from ai_service_client.models.generate_response import GenerateResponse


def test_generate_response_success() -> None:
    """Adapter returns result from generated client response."""
    svc = ServiceClient(base_url="http://example.com")

    mock_response = GenerateResponse(result="ok")

    with patch(
        "ai_adapter.client_impl.generate_generate_post.sync",
        return_value=mock_response,
    ):
        result = svc.generate_response("hi", "be short")

    assert result == "ok"


def test_generate_response_validation_error_raises() -> None:
    """Adapter raises when service returns validation error."""
    from ai_service_client.models.http_validation_error import HTTPValidationError

    svc = ServiceClient(base_url="http://example.com")

    with (
        patch(
            "ai_adapter.client_impl.generate_generate_post.sync",
            return_value=HTTPValidationError(detail=[]),
        ),
        pytest.raises(TypeError, match="Validation error"),
    ):
        svc.generate_response("hi", "be short")


def test_generate_response_none_raises() -> None:
    """Adapter raises when service returns None."""
    svc = ServiceClient(base_url="http://example.com")

    with (
        patch(
            "ai_adapter.client_impl.generate_generate_post.sync",
            return_value=None,
        ),
        pytest.raises(RuntimeError, match="No response"),
    ):
        svc.generate_response("hi", "be short")


def test_register_sets_get_client() -> None:
    """Register wires ai_api.get_client to ServiceClient."""
    import ai_adapter
    import ai_api

    ai_adapter.register(base_url="http://example.com")
    client = ai_api.get_client()
    assert isinstance(client, ServiceClient)
