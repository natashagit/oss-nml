"""OpenAI Client Implementation.

This module provides a concrete implementation of the AI client API using OpenAI's API.
It retrieves user-specific OpenAI API keys from multiple sources with the following priority:
1. Explicit openai_api_key parameter
2. OPENAI_API_KEY environment variable
3. Database (CredentialStore)

This allows for flexible deployment scenarios while maintaining OAuth support.
"""

import logging
import os
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

import ai_client_api
from openai import OpenAI, Stream

from openai_client_impl.database import CredentialStore

if TYPE_CHECKING:
    from openai.types.chat import ChatCompletion, ChatCompletionChunk

logger = logging.getLogger(__name__)


class OpenAIClient(ai_client_api.Client):
    """Concrete implementation of the AI Client abstraction using OpenAI's API.

    This class provides a complete implementation of the ai_client_api.Client abstraction
    using OpenAI's chat completion API. It retrieves user-specific OpenAI API keys from
    the database and uses them to authenticate requests.

    Attributes:
        user_id: The unique identifier for the user.
        credential_store: Database store for retrieving user credentials.
        openai_client: The OpenAI API client instance.

    """

    def __init__(
        self,
        user_id: str,
        credential_store: CredentialStore | None = None,
        openai_api_key: str | None = None,
    ) -> None:
        """Initialize the OpenAIClient for a specific user.

        API key is resolved in the following priority order:
        1. Explicit openai_api_key parameter
        2. OPENAI_API_KEY environment variable
        3. Database (CredentialStore)

        Args:
            user_id: The unique identifier for the user.
            credential_store: Optional CredentialStore instance. If not provided,
                             a new one will be created.
            openai_api_key: Optional OpenAI API key. If provided, uses this directly.
                           Useful for testing or when not using database storage.

        Raises:
            ValueError: If no OpenAI API key is found from any source.

        """
        self.user_id = user_id
        # Defer database initialization unless we actually need it
        self.credential_store = credential_store

        # Get API key in priority order: parameter -> environment -> database
        if openai_api_key:
            api_key = openai_api_key
            logger.debug("Using API key from parameter for user %s", user_id)
        else:
            # Try environment variable first
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                logger.debug("Using API key from environment variable for user %s", user_id)
            else:
                # Fall back to database (initialize store only when needed)
                if self.credential_store is None:
                    self.credential_store = CredentialStore()
                api_key = self.credential_store.get_openai_api_key(user_id)
                if api_key:
                    logger.debug("Using API key from database for user %s", user_id)

        if not api_key:
            msg = (
                f"No OpenAI API key found for user {user_id}. "
                "Please provide openai_api_key parameter, set OPENAI_API_KEY environment variable, "
                "or configure credentials in the database."
            )
            raise ValueError(msg)

        # Support optional project/org scoping if provided via environment
        project = os.getenv("OPENAI_PROJECT")
        organization = os.getenv("OPENAI_ORG")
        if project or organization:
            self.openai_client = OpenAI(api_key=api_key, project=project, organization=organization)
        else:
            self.openai_client = OpenAI(api_key=api_key)
        logger.info("Initialized OpenAI client for user %s", user_id)

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        """Generate a chat completion using OpenAI's API.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
                     Role can be 'system', 'user', or 'assistant'.
            model: The OpenAI model to use (e.g., 'gpt-3.5-turbo', 'gpt-4').
            temperature: Sampling temperature between 0.0 and 2.0.
                        Higher values make output more random.
            max_tokens: Maximum number of tokens to generate.

        Returns:
            A dictionary containing the completion response with keys:
                - message: dict with 'role' and 'content'
                - model: the model used
                - usage: dict with token counts
                - finish_reason: why the model stopped

        Raises:
            Exception: If the API request fails.

        """
        try:
            logger.debug(
                "Requesting chat completion for user %s with model %s", self.user_id, model,
            )

            response: ChatCompletion = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,  # type: ignore[arg-type]
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Extract the response
            choice = response.choices[0]
            message = choice.message

            result = {
                "message": {"role": message.role, "content": message.content or ""},
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
                "finish_reason": choice.finish_reason,
            }

        except Exception:
            logger.exception("Failed to generate chat completion for user %s", self.user_id)
            raise
        else:
            logger.info(
                "Chat completion successful for user %s. Tokens used: %s",
                self.user_id,
                result["usage"]["total_tokens"],
            )
            return result

    def chat_completion_stream(
        self,
        messages: list[dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> Iterator[dict[str, Any]]:
        """Generate a streaming chat completion using OpenAI's API.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            model: The OpenAI model to use.
            temperature: Sampling temperature between 0.0 and 2.0.
            max_tokens: Maximum number of tokens to generate.

        Yields:
            Dictionaries containing chunk information:
                - content: The text delta for this chunk
                - finish_reason: Reason for stopping (present in final chunk)
                - model: The model being used

        Raises:
            Exception: If the API request fails.

        """
        try:
            logger.debug(
                "Requesting streaming chat completion for user %s with model %s",
                self.user_id,
                model,
            )

            stream: Stream[ChatCompletionChunk] = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,  # type: ignore[arg-type]
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            for chunk in stream:
                if not chunk.choices:
                    continue

                choice = chunk.choices[0]
                delta = choice.delta

                result: dict[str, Any] = {
                    "content": delta.content or "",
                    "finish_reason": choice.finish_reason,
                    "model": chunk.model,
                }

                yield result

            logger.info("Streaming chat completion completed for user %s", self.user_id)

        except Exception:
            logger.exception(
                "Failed to generate streaming chat completion for user %s",
                self.user_id,
            )
            raise


def get_client_impl(
    user_id: str,
    credential_store: CredentialStore | None = None,
    openai_api_key: str | None = None,
) -> ai_client_api.Client:
    """Return a configured OpenAIClient instance for a specific user.

    Args:
        user_id: The unique identifier for the user.
        credential_store: Optional CredentialStore instance.
        openai_api_key: Optional OpenAI API key. If not provided, will check
                       environment variable and database.

    Returns:
        An OpenAIClient instance configured for the user.

    """
    return OpenAIClient(
        user_id=user_id,
        credential_store=credential_store,
        openai_api_key=openai_api_key,
    )


def register(
    credential_store: CredentialStore | None = None,
    openai_api_key: str | None = None,
) -> None:
    """Register the OpenAI client implementation with the AI client API.

    Args:
        credential_store: Optional CredentialStore instance to use globally.
        openai_api_key: Optional OpenAI API key to use globally.
                        If not provided, will check environment variable and database.

    """

    def _get_client(user_id: str) -> ai_client_api.Client:
        return get_client_impl(
            user_id=user_id,
            credential_store=credential_store,
            openai_api_key=openai_api_key,
        )

    ai_client_api.get_client = _get_client
