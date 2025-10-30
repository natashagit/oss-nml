"""FastAPI application for AI client service."""

import logging
from collections.abc import Iterator
from typing import Annotated

import openai_client_impl  # noqa: F401 - Registers the OpenAI client implementation
from ai_client_api import Client
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from openai_client_impl import CredentialStore, OAuthManager

from ai_client_service.dependencies import get_ai_client, get_credential_store
from ai_client_service.models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionStreamChunk,
    ChatMessage,
    HealthCheckResponse,
    OAuthCallbackRequest,
    OAuthCallbackResponse,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Client Service",
    description="RESTful API for AI client operations with OAuth 2.0 authentication",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> HealthCheckResponse:
    """Health check endpoint.

    Returns:
        HealthCheckResponse: Service health status.

    """
    return HealthCheckResponse(status="healthy", version="0.1.0")


@app.get("/oauth/authorize")
def oauth_authorize() -> RedirectResponse:
    """Initiate OAuth 2.0 authorization flow.

    Returns:
        RedirectResponse: Redirect to OAuth provider.

    """
    try:
        oauth_manager = OAuthManager()
        auth_url = oauth_manager.get_authorization_url()
        logger.info("Redirecting user to OAuth provider: %s", auth_url)
        return RedirectResponse(url=auth_url)
    except Exception as e:
        logger.exception("Failed to initiate OAuth flow")
        raise HTTPException(status_code=500, detail=f"Failed to initiate OAuth flow: {e!s}") from e


@app.post("/oauth/callback")
def oauth_callback(
    callback_data: OAuthCallbackRequest,
    credential_store: Annotated[CredentialStore, Depends(get_credential_store)],
) -> OAuthCallbackResponse:
    """Handle OAuth 2.0 callback.

    Args:
        callback_data: OAuth callback data.
        credential_store: Credential store dependency.

    Returns:
        OAuthCallbackResponse: OAuth callback result.

    """
    try:
        oauth_manager = OAuthManager()
        user_id, tokens = oauth_manager.handle_callback(
            callback_data.code, callback_data.state,
        )

        # Store the tokens in the credential store
        credential_store.store_google_tokens(user_id, tokens)

        logger.info("OAuth callback successful for user %s", user_id)
        return OAuthCallbackResponse(
            success=True,
            message="OAuth authentication successful",
            user_id=user_id,
        )
    except Exception as e:
        logger.exception("OAuth callback failed")
        return OAuthCallbackResponse(
            success=False,
            message=f"OAuth authentication failed: {e!s}",
            user_id=None,
        )


@app.post("/chat/completions")
def create_chat_completion(
    request: ChatCompletionRequest,
    user_id: Annotated[str, Query(description="User ID for authentication")],
    client: Annotated[Client, Depends(get_ai_client)],
) -> ChatCompletionResponse:
    """Create a chat completion.

    Args:
        request: Chat completion request data.
        user_id: User ID for authentication.
        client: Injected AI client instance.

    Returns:
        ChatCompletionResponse: Chat completion result.

    Raises:
        HTTPException: If the request fails.

    """
    try:
        # Convert Pydantic models to dict format expected by the client
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        logger.info("Creating chat completion for user %s with model %s", user_id, request.model)

        response = client.chat_completion(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        # Convert response to our Pydantic model
        message = ChatMessage(
            role=response["message"]["role"],
            content=response["message"]["content"],
        )

        return ChatCompletionResponse(
            message=message,
            model=response["model"],
            usage=response["usage"],
            finish_reason=response["finish_reason"],
        )
    except Exception as e:
        logger.exception("Failed to create chat completion for user %s", user_id)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create chat completion: {e!s}",
        ) from e


@app.post("/chat/completions/stream")
def create_chat_completion_stream(
    request: ChatCompletionRequest,
    user_id: Annotated[str, Query(description="User ID for authentication")],
    client: Annotated[Client, Depends(get_ai_client)],
) -> Iterator[ChatCompletionStreamChunk]:
    """Create a streaming chat completion.

    Args:
        request: Chat completion request data.
        user_id: User ID for authentication.
        client: Injected AI client instance.

    Yields:
        ChatCompletionStreamChunk: Streaming chunks of the completion.

    Raises:
        HTTPException: If the request fails.

    """
    try:
        # Convert Pydantic models to dict format expected by the client
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        logger.info(
            "Creating streaming chat completion for user %s with model %s",
            user_id,
            request.model,
        )

        for chunk_data in client.chat_completion_stream(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        ):
            chunk = ChatCompletionStreamChunk(
                content=chunk_data["content"],
                finish_reason=chunk_data["finish_reason"],
                model=chunk_data["model"],
            )
            yield chunk
    except Exception as e:
        logger.exception("Failed to create streaming chat completion for user %s", user_id)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create streaming chat completion: {e!s}",
        ) from e




if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)  # noqa: S104
