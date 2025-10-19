"""Dependency injection for mail client service."""

from collections.abc import Callable

from mail_client_api import Client, get_client


# Global client factory - can be overridden for testing
def _client_factory() -> Client:
    return get_client(interactive=False)


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
