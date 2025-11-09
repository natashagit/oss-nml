"""Service client implementation for AI client adapter."""

from collections.abc import Iterator

from ai_client_api import Client
from ai_client_api.models import (
    ChatCompletionChunk,
    ChatCompletionResponse,
    ChatMessage,
    TokenUsage,
)
from ai_client_service_client.api.default import (
    create_chat_completion_chat_completions_post,
)
from ai_client_service_client.client import Client as GeneratedClient
from ai_client_service_client.models.chat_completion_request import ChatCompletionRequest
from ai_client_service_client.models.chat_message import ChatMessage as ServiceChatMessage


class ServiceClient(Client):
    """Client implementation that wraps the generated AI client service API."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        user_id: str = "default_user",
    ) -> None:
        """Initialize the service client.

        Args:
            base_url: The base URL of the AI client service.
            user_id: The user ID for authentication.

        """
        self.base_url = base_url
        self.user_id = user_id
        self.client = GeneratedClient(base_url=base_url)

    def chat_completion(
        self,
        messages: list[ChatMessage],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> ChatCompletionResponse:
        """Generate a chat completion using the AI service.

        Args:
            messages: List of chat messages.
            model: The model to use for completion.
            temperature: Sampling temperature (0.0 to 2.0).
            max_tokens: Maximum tokens to generate.

        Returns:
            A chat completion response.

        """
        # Convert domain ChatMessage to service ChatMessage
        service_messages = [
            ServiceChatMessage(role=msg.role, content=msg.content)
            for msg in messages
        ]

        request = ChatCompletionRequest(
            messages=service_messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        response = create_chat_completion_chat_completions_post.sync(
            client=self.client,
            user_id=self.user_id,
            body=request,
        )

        # Handle error responses
        if response is None:
            raise ValueError("Received None response from service")
        
        # Check if it's an HTTPValidationError (imported from generated client)
        from ai_client_service_client.models.http_validation_error import HTTPValidationError
        if isinstance(response, HTTPValidationError):
            raise ValueError(f"Validation error: {response}")

        # Convert service response to domain models
        finish_reason: str | None = None
        if hasattr(response.finish_reason, "__class__"):
            # Handle Unset type from generated client
            from ai_client_service_client.types import Unset
            if not isinstance(response.finish_reason, Unset):
                finish_reason = str(response.finish_reason) if response.finish_reason is not None else None
        else:
            finish_reason = str(response.finish_reason) if response.finish_reason is not None else None

        # Access usage as dictionary (ChatCompletionResponseUsage uses additional_properties)
        # The usage object supports dictionary-like access via __getitem__
        prompt_tokens = response.usage["prompt_tokens"] if "prompt_tokens" in response.usage else 0
        completion_tokens = response.usage["completion_tokens"] if "completion_tokens" in response.usage else 0
        total_tokens = response.usage["total_tokens"] if "total_tokens" in response.usage else 0

        return ChatCompletionResponse(
            message=ChatMessage(
                role=response.message.role,
                content=response.message.content,
            ),
            model=response.model,
            usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
            ),
            finish_reason=finish_reason,
        )

    def chat_completion_stream(
        self,
        messages: list[ChatMessage],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> Iterator[ChatCompletionChunk]:
        """Generate a streaming chat completion using the AI service.

        Args:
            messages: List of chat messages.
            model: The model to use for completion.
            temperature: Sampling temperature (0.0 to 2.0).
            max_tokens: Maximum tokens to generate.

        Yields:
            Chunks of the completion response as they're generated.

        """
        # Convert domain ChatMessage to service ChatMessage
        service_messages = [
            ServiceChatMessage(role=msg.role, content=msg.content)
            for msg in messages
        ]

        request = ChatCompletionRequest(
            messages=service_messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # For now, we'll use the regular chat completion and simulate streaming
        # In a real implementation, this would use the streaming endpoint
        response = create_chat_completion_chat_completions_post.sync(
            client=self.client,
            user_id=self.user_id,
            body=request,
        )

        # Handle error responses
        if response is None:
            yield ChatCompletionChunk(
                content="No response",
                finish_reason="stop",
                model=model,
            )
            return
        
        # Check if it's an HTTPValidationError
        from ai_client_service_client.models.http_validation_error import HTTPValidationError
        if isinstance(response, HTTPValidationError):
            yield ChatCompletionChunk(
                content=f"Validation error: {response}",
                finish_reason="stop",
                model=model,
            )
            return

        # Simulate streaming by yielding the response as a single chunk
        finish_reason: str | None = None
        if hasattr(response.finish_reason, "__class__"):
            from ai_client_service_client.types import Unset
            if not isinstance(response.finish_reason, Unset):
                finish_reason = str(response.finish_reason) if response.finish_reason is not None else None
        else:
            finish_reason = str(response.finish_reason) if response.finish_reason is not None else None

        yield ChatCompletionChunk(
            content=response.message.content,
            finish_reason=finish_reason,
            model=response.model,
        )

    def get_client(self) -> GeneratedClient:
        """Get the underlying generated client.

        Returns:
            The generated client instance.

        """
        return self.client
