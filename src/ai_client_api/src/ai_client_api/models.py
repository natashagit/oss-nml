"""Domain models for AI client API - implementation-agnostic types."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ChatMessage:
    """A single message in a chat conversation.

    Attributes:
        role: The role of the message sender (e.g., 'system', 'user', 'assistant').
        content: The content of the message.

    """

    role: str
    content: str


@dataclass(frozen=True)
class TokenUsage:
    """Token usage information for a completion.

    Attributes:
        prompt_tokens: Number of tokens in the prompt.
        completion_tokens: Number of tokens in the completion.
        total_tokens: Total number of tokens used.

    """

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass(frozen=True)
class ChatCompletionResponse:
    """Response from a chat completion request.

    Attributes:
        message: The assistant's message response.
        model: The model used for generation.
        usage: Token usage information.
        finish_reason: Reason why the model stopped generating (e.g., 'stop', 'length').

    """

    message: ChatMessage
    model: str
    usage: TokenUsage
    finish_reason: str | None = None


@dataclass(frozen=True)
class ChatCompletionChunk:
    """A chunk from a streaming chat completion.

    Attributes:
        content: The text delta for this chunk.
        finish_reason: Reason for stopping (present in final chunk only).
        model: The model being used.

    """

    content: str
    finish_reason: str | None = None
    model: str | None = None

