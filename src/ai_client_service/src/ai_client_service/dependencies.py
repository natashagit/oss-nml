"""Dependency injection for AI client service."""

import logging
from collections.abc import Callable

from ai_client_api import Client, get_client
from openai_client_impl import CredentialStore, OpenAIClient

logger = logging.getLogger(__name__)

# Global client factory - can be overridden for testing
def _client_factory() -> Client:
    """Return default client factory that uses the registered implementation."""
    return get_client(user_id="default_user")  # This will be overridden with actual user_id


def get_ai_client(user_id: str) -> Client:
    """Create and return an AI client for the given user."""
    try:
        client = OpenAIClient(user_id=user_id)
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
    _client_factory = factory


def get_credential_store() -> CredentialStore:
    """Get a credential store instance.

    Returns:
        CredentialStore: A credential store instance for managing user credentials.

    """
    return CredentialStore()
