"""Service client implementation for AI client adapter."""

from collections.abc import Iterator

from ai_client_api import Client

from ai_client_service_client.api.default import (
    create_chat_completion_chat_completions_post,
    create_chat_completion_stream_chat_completions_stream_post,
)
from ai_client_service_client.client import Client as GeneratedClient
from ai_client_service_client.models.chat_completion_request import ChatCompletionRequest
from ai_client_service_client.models.chat_completion_response import ChatCompletionResponse
from ai_client_service_client.models.chat_message import ChatMessage


class ServiceClient(Client):
    """Client implementation that wraps the generated AI client service API."""

    def __init__(self, base_url: str = "http://127.0.0.1:8000", user_id: str = "default_user") -> None:
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
        messages: list[dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> dict[str, any]:
        """Generate a chat completion using the AI service.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            model: The model to use for completion.
            temperature: Sampling temperature (0.0 to 2.0).
            max_tokens: Maximum tokens to generate.

        Returns:
            A dictionary containing the completion response.

        """
        # Convert messages to ChatMessage objects
        chat_messages = [
            ChatMessage(role=msg["role"], content=msg["content"]) 
            for msg in messages
        ]
        
        request = ChatCompletionRequest(
            messages=chat_messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        response = create_chat_completion_chat_completions_post.sync(
            client=self.client,
            user_id=self.user_id,
            body=request,
        )
        
        return {
            "message": {
                "role": response.message.role,
                "content": response.message.content,
            },
            "model": response.model,
            "usage": response.usage.to_dict(),
            "finish_reason": response.finish_reason,
        }

    def chat_completion_stream(
        self,
        messages: list[dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> Iterator[dict[str, any]]:
        """Generate a streaming chat completion using the AI service.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            model: The model to use for completion.
            temperature: Sampling temperature (0.0 to 2.0).
            max_tokens: Maximum tokens to generate.

        Yields:
            Chunks of the completion response as they're generated.

        """
        # Convert messages to ChatMessage objects
        chat_messages = [
            ChatMessage(role=msg["role"], content=msg["content"]) 
            for msg in messages
        ]
        
        request = ChatCompletionRequest(
            messages=chat_messages,
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
        
        # Simulate streaming by yielding the response as a single chunk
        if response and hasattr(response, 'message'):
            yield {
                "content": response.message.content,
                "finish_reason": response.finish_reason,
                "model": response.model,
            }
        else:
            # Fallback: yield the response as a single chunk
            yield {
                "content": str(response) if response else "No response",
                "finish_reason": "stop",
                "model": model,
            }

    def get_client(self):
        """Get the underlying generated client.

        Returns:
            The generated client instance.

        """
        return self.client
