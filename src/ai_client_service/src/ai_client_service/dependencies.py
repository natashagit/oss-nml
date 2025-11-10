"""Dependency injection for AI client service."""

import logging
from collections.abc import Callable

from ai_client_api import (  # type: ignore[attr-defined]  # Exported via __init__.py
    Client,
    get_client,
)
from fastapi import Depends, HTTPException
from openai_client_impl import OpenAIClient
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


def require_authentication(request: Request) -> str:
    """Dependency to require OAuth authentication.

    Checks if the user is authenticated via OAuth by verifying user_id in session.

    Args:
        request: FastAPI request object for session access.

    Returns:
        str: The authenticated user's ID.

    Raises:
        HTTPException: If the user is not authenticated.

    """
    user_id: str | None = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please complete OAuth flow first.",
        )
    return user_id


def require_authenticated_client(
    request: Request,
    user_id: str = Depends(require_authentication),
) -> Client:
    """Dependency to require authentication and API key, returning an AI client.

    This dependency:
    1. Requires OAuth authentication (via require_authentication)
    2. Verifies OpenAI API key is set in session
    3. Returns a configured AI client

    Args:
        user_id: The authenticated user's ID (from require_authentication).
        request: FastAPI request object for session access.

    Returns:
        Client: A configured AI client instance.

    Raises:
        HTTPException: If authentication fails or API key is not set.

    """
    # Check if API key is set
    openai_api_key = request.session.get("openai_api_key")
    if not openai_api_key:
        raise HTTPException(
            status_code=400,
            detail="OpenAI API key not set. Please set your API key using POST /api-keys",
        )

    try:
        return get_ai_client(user_id=user_id, request=request)
    except Exception as e:
        logger.exception("Failed to create AI client for user %s", user_id)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create AI client: {e!s}",
        ) from e

