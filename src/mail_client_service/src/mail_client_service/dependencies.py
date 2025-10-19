"""Dependency injection for mail client service."""

from collections.abc import Callable

import gmail_client_impl  # Import to ensure Gmail client is available
from mail_client_api import Client


# Global client factory - can be overridden for testing
def _client_factory() -> Client:
    # Use Gmail client directly instead of going through dependency injection
    # This prevents circular dependency where service would call itself
    return gmail_client_impl.GmailClient(interactive=True)


def get_mail_client() -> Client:
    """Return a mail client instance using the configured factory.

    This function is designed to be used with FastAPI's dependency injection system.

    Returns:
        Client: An instance of the mail client.

    """
    return _client_factory()


def set_client_factory(factory: Callable[[], Client]) -> None:
    """Override the client factory (primarily for testing).

    Args:
        factory: A callable that returns a Client instance.

    """
    global _client_factory  # noqa: PLW0603
    _client_factory = factory
