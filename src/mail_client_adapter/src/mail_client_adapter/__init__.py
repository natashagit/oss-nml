"""Mail client adapter package providing a ServiceClient implementation."""

import mail_client_api

from .client_impl import MessageDetailAdapter, MessageSummaryAdapter, ServiceClient


def get_client_impl(*, interactive: bool = False) -> mail_client_api.Client:  # noqa: ARG001
    """Return a configured ServiceClient instance.

    Args:
        interactive: Unused parameter, kept for API compatibility.

    """
    return ServiceClient()


def register() -> None:
    """Register the service client implementation with the mail client API."""
    mail_client_api.get_client = get_client_impl


def get_client(base_url: str = "http://127.0.0.1:8000") -> ServiceClient:
    """Drop-in replacement for mail_client_api.get_client."""
    return ServiceClient(base_url=base_url)


__all__ = ["MessageDetailAdapter", "MessageSummaryAdapter", "ServiceClient", "get_client", "get_client_impl", "register"]
