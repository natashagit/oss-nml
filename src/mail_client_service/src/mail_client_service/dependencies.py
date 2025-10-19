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
        
    Raises:
        HTTPException: If client initialization fails due to missing credentials.

    """
    try:
        return _client_factory()
    except (FileNotFoundError, RuntimeError) as e:
        from fastapi import HTTPException
        if "No valid credentials found" in str(e) or "credentials.json" in str(e):
            raise HTTPException(
                status_code=503, 
                detail="Mail service unavailable: Gmail credentials not configured. Please configure Gmail authentication."
            ) from e
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize mail client: {e!s}"
        ) from e


def set_client_factory(factory: Callable[[], Client]) -> None:
    """Override the client factory (primarily for testing).

    Args:
        factory: A callable that returns a Client instance.

    """
    global _client_factory  # noqa: PLW0603
    _client_factory = factory
