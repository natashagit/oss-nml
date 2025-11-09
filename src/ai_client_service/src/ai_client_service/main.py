"""FastAPI application for AI client service."""

import logging
import os
import secrets
from collections.abc import Iterator
from typing import Annotated

import openai_client_impl  # noqa: F401 - Registers the OpenAI client implementation
from ai_client_api import Client
from ai_client_api.models import ChatMessage as APIChatMessage
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from openai_client_impl import OAuthManager
from starlette.middleware.sessions import SessionMiddleware

from ai_client_service.dependencies import get_ai_client
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

# Configure session middleware
session_secret_key = os.environ.get("SESSION_SECRET_KEY", secrets.token_urlsafe(32))
app.add_middleware(
    SessionMiddleware,
    secret_key=session_secret_key,
    same_site="lax",
    https_only=False,  # Allow HTTP for local development
)

# Enable insecure transport for local OAuth (HTTP instead of HTTPS)
os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")


@app.get("/health")
def health_check() -> HealthCheckResponse:
    """Health check endpoint.

    Returns:
        HealthCheckResponse: Service health status.

    """
    return HealthCheckResponse(status="healthy", version="0.1.0")


@app.get("/oauth/authorize")
def oauth_authorize(request: Request) -> RedirectResponse:
    """Initiate OAuth 2.0 authorization flow.

    Args:
        request: FastAPI request object for session access.

    Returns:
        RedirectResponse: Redirect to OAuth provider.

    """
    try:
        # Generate state parameter for CSRF protection
        state = secrets.token_urlsafe(32)
        request.session["oauth_state"] = state

        oauth_manager = OAuthManager(credential_store=None)
        auth_url, _ = oauth_manager.get_authorization_url(state=state)
        logger.info("Redirecting user to OAuth provider: %s", auth_url)
        return RedirectResponse(url=auth_url)
    except Exception as e:
        logger.exception("Failed to initiate OAuth flow")
        raise HTTPException(status_code=500, detail=f"Failed to initiate OAuth flow: {e!s}") from e


@app.get("/oauth/callback")
def oauth_callback(
    request: Request,
    code: Annotated[str | None, Query(description="Authorization code from OAuth provider")] = None,
    state: Annotated[str | None, Query(description="State parameter for CSRF protection")] = None,
    error: Annotated[str | None, Query(description="Error from OAuth provider")] = None,
) -> OAuthCallbackResponse:
    """Handle OAuth 2.0 callback.

    Args:
        request: FastAPI request object for session access.
        code: Authorization code from OAuth provider.
        state: State parameter for CSRF protection.
        error: Error from OAuth provider if any.

    Returns:
        OAuthCallbackResponse: OAuth callback result.

    """
    try:
        # Check for OAuth errors
        if error:
            logger.warning("OAuth error received: %s", error)
            return OAuthCallbackResponse(
                success=False,
                message=f"OAuth authentication failed: {error}",
                user_id=None,
            )

        if not code:
            return OAuthCallbackResponse(
                success=False,
                message="Missing authorization code",
                user_id=None,
            )

        # Verify state parameter
        stored_state = request.session.get("oauth_state")
        if not state or state != stored_state:
            logger.warning("OAuth state mismatch - possible CSRF attack")
            return OAuthCallbackResponse(
                success=False,
                message="Invalid state parameter",
                user_id=None,
            )

        # Construct the full callback URL for OAuthManager
        callback_url = str(request.url)

        oauth_manager = OAuthManager(credential_store=None)
        user_info = oauth_manager.handle_callback(
            authorization_response=callback_url,
            state=state,
        )

        # Store user info and tokens in session
        user_id = user_info["user_id"]
        request.session["user_id"] = user_id
        request.session["user_email"] = user_info.get("email")
        # Note: We don't store access_token/refresh_token in session as they're not needed
        # for OpenAI API calls. If needed later, we can add them.

        # Clear the OAuth state
        request.session.pop("oauth_state", None)

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
    http_request: Request,
    user_id: Annotated[str, Query(description="User ID for authentication")],
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
        # Get client with session access
        client = get_ai_client(user_id=user_id, request=http_request)

        # Convert Pydantic models to domain ChatMessage dataclasses
        messages = [APIChatMessage(role=msg.role, content=msg.content) for msg in request.messages]

        logger.info("Creating chat completion for user %s with model %s", user_id, request.model)

        response = client.chat_completion(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        # Convert domain response to Pydantic model
        message = ChatMessage(
            role=response.message.role,
            content=response.message.content,
        )

        return ChatCompletionResponse(
            message=message,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            finish_reason=response.finish_reason,
        )
    except Exception as e:
        logger.exception("Failed to create chat completion for user %s", user_id)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create chat completion: {e!s}",
        ) from e


@app.post("/chat/completions/stream", response_model=None)
def create_chat_completion_stream(
    request: ChatCompletionRequest,
    http_request: Request,
    user_id: Annotated[str, Query(description="User ID for authentication")],
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
        # Get client with session access
        client = get_ai_client(user_id=user_id, request=http_request)

        # Convert Pydantic models to domain ChatMessage dataclasses
        messages = [APIChatMessage(role=msg.role, content=msg.content) for msg in request.messages]

        logger.info(
            "Creating streaming chat completion for user %s with model %s",
            user_id,
            request.model,
        )

        for chunk in client.chat_completion_stream(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        ):
            yield ChatCompletionStreamChunk(
                content=chunk.content,
                finish_reason=chunk.finish_reason,
                model=chunk.model or request.model,
            )
    except Exception as e:
        logger.exception("Failed to create streaming chat completion for user %s", user_id)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create streaming chat completion: {e!s}",
        ) from e




if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)  # noqa: S104
