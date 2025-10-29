"""AI Client Adapter for service client operations."""

import ai_client_api

from ai_client_adapter.client_impl import ServiceClient


def get_client_impl(user_id: str) -> ai_client_api.Client:
    """Return a configured ServiceClient instance.

    Args:
        user_id: The unique identifier for the user.

    """
    return ServiceClient(user_id=user_id)


def register() -> None:
    """Register the service client implementation with the AI client API."""
    ai_client_api.get_client = get_client_impl


def get_client(base_url: str = "http://127.0.0.1:8000", user_id: str = "default_user") -> ServiceClient:
    """Drop-in replacement for ai_client_api.get_client."""
    return ServiceClient(base_url=base_url, user_id=user_id)


# Auto-register the adapter when the module is imported
register()


__all__ = ["ServiceClient", "get_client", "get_client_impl", "register"]
