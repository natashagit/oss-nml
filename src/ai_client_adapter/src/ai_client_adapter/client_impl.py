"""Service client implementation for AI client adapter (temporary stub)."""

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from ai_client_api import Client

if TYPE_CHECKING:
    # Type-only import so runtime doesn't require the generated package yet.
    from ai_client_service_client import Client as GeneratedClient
else:
    # Narrow the ignore to the specific mypy assignment rule.
    GeneratedClient = Any  # type: ignore[assignment]


class ServiceClient(Client):
    """Client implementation that will wrap the generated AI client service API.

    Until the generated client/wiring is ready, tests expect NotImplementedError.
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        user_id: str = "default_user",
    ) -> None:
        """Create a lightweight, test-friendly service client stub.

        This stub intentionally does not open network connections.
        """
        self.base_url = base_url
        self.user_id = user_id
        # Intentionally do NOT construct a real HTTP client yet.

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        """Generate a chat completion (not implemented yet)."""
        msg = "Service client not yet generated"
        raise NotImplementedError(msg)

    def chat_completion_stream(
        self,
        messages: list[dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> Iterator[dict[str, Any]]:
        """Stream a chat completion (not implemented yet)."""
        msg = "Service client not yet generated"
        raise NotImplementedError(msg)

    def get_client(self) -> "GeneratedClient":
        """Get the underlying generated client (not implemented yet)."""
        msg = "Service client not yet generated"
        raise NotImplementedError(msg)
