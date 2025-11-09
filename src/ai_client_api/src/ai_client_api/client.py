"""Core AI client contract definitions and factory placeholder."""

from abc import ABC, abstractmethod
from collections.abc import Iterator

from ai_client_api.models import (
    ChatCompletionChunk,
    ChatCompletionResponse,
    ChatMessage,
)


class Client(ABC):
    """Abstract base class representing an AI client for chat completions."""

    @abstractmethod
    def chat_completion(
        self,
        messages: list[ChatMessage],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> ChatCompletionResponse:
        """Generate a chat completion.

        Args:
            messages: List of chat messages.
            model: The model to use for completion.
            temperature: Sampling temperature (0.0 to 2.0).
            max_tokens: Maximum tokens to generate.

        Returns:
            A chat completion response.

        """
        raise NotImplementedError

    @abstractmethod
    def chat_completion_stream(
        self,
        messages: list[ChatMessage],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> Iterator[ChatCompletionChunk]:
        """Generate a streaming chat completion.

        Args:
            messages: List of chat messages.
            model: The model to use for completion.
            temperature: Sampling temperature (0.0 to 2.0).
            max_tokens: Maximum tokens to generate.

        Yields:
            Chunks of the completion response as they're generated.

        """
        raise NotImplementedError


def get_client(user_id: str) -> Client:
    """Return an instance of an AI Client for the specified user.

    Args:
        user_id: The unique identifier for the authenticated user.

    Returns:
        A configured Client instance.

    """
    raise NotImplementedError
