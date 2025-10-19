"""Mail client adapter package providing a ServiceClient implementation."""

import mail_client_api

from .client_impl import MessageDetailAdapter, MessageSummaryAdapter, ServiceClient


def get_client_impl(*, interactive: bool = False) -> mail_client_api.Client:
    """Return a configured ServiceClient instance."""
    return ServiceClient()


def register() -> None:
    """Register the service client implementation with the mail client API."""
    mail_client_api.get_client = get_client_impl


def get_client(base_url: str = "http://127.0.0.1:8000") -> ServiceClient:
    """Drop-in replacement for mail_client_api.get_client."""
    return ServiceClient(base_url=base_url)


__all__ = ["MessageDetailAdapter", "MessageSummaryAdapter", "ServiceClient", "get_client", "get_client_impl", "register"]


# Dependency Injection happens at import time
# Only register if explicitly requested (not auto-register)
# register()  # Commented out to prevent auto-registration
