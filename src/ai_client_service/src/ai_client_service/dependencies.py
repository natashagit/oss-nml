"""Dependency injection for AI client service."""

import logging
from collections.abc import Callable
from typing import TYPE_CHECKING

from ai_client_api import Client, get_client
from openai_client_impl import OpenAIClient

if TYPE_CHECKING:
    from starlette.requests import Request

logger = logging.getLogger(__name__)

# Global client factory - can be overridden for testing
def _client_factory(user_id: str) -> Client:
    """Return default client factory that uses the registered implementation."""
    return get_client(user_id=user_id)


def get_ai_client(user_id: str, request: "Request | None" = None) -> Client:
    """Return an AI client instance for a specific user.

    This function is designed to be used with FastAPI's dependency injection system.
    The client will resolve credentials in priority order:
    1. Session (openai_api_key from request.session)
    2. OPENAI_API_KEY environment variable

    Args:
        user_id: The unique identifier for the user.
        request: Optional FastAPI request object for session access.

    Returns:
        Client: An instance of the AI client.

    Raises:
        ValueError: If no credentials are found for the user.

    """
    try:
        # Get API key from session if available
        openai_api_key = None
        if request:
            openai_api_key = request.session.get("openai_api_key")

        # OpenAIClient will check parameter, then environment variable
        client = OpenAIClient(user_id=user_id, openai_api_key=openai_api_key)
    except Exception:
        logger.exception("Failed to create AI client for user %s", user_id)
        raise
    else:
        logger.info("Successfully created AI client for user %s", user_id)
        return client

def set_client_factory(factory: Callable[[str], Client]) -> None:
    """Override the client factory (primarily for testing).

    Args:
        factory: A callable that takes a user_id and returns a Client instance.

    """
    global _client_factory  # noqa: PLW0603
    _client_factory = factory  # type: ignore[assignment]

