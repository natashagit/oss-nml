"""Service client implementation for AI client adapter (temporary stub)."""

from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional

from ai_client_api import Client

if TYPE_CHECKING:
    # Type-only import so runtime doesn't require the generated package yet.
    from ai_client_service_client import Client as GeneratedClient
else:
    GeneratedClient = Any  # type: ignore


class ServiceClient(Client):
    """Client implementation that will wrap the generated AI client service API.

    Until the generated client/wiring is ready, tests expect NotImplementedError.
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        user_id: str = "default_user",
    ) -> None:
        self.base_url = base_url
        self.user_id = user_id
        # Intentionally do NOT construct a real HTTP client yet.

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Generate a chat completion (not implemented yet)."""
        raise NotImplementedError("Service client not yet generated")

    def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Iterator[Dict[str, Any]]:
        """Stream a chat completion (not implemented yet)."""
        raise NotImplementedError("Service client not yet generated")

    def get_client(self) -> "GeneratedClient":
        """Get the underlying generated client (not implemented yet)."""
        raise NotImplementedError("Service client not yet generated")
