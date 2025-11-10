"""FastAPI application for AI client service."""

import logging
import os
import secrets
from collections.abc import Iterator
from typing import Annotated

import openai_client_impl  # noqa: F401 - Registers the OpenAI client implementation
from ai_client_api import Client  # type: ignore[attr-defined]  # Client is exported via __init__.py
from ai_client_api.models import ChatMessage as APIChatMessage
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from openai_client_impl import CredentialStore, OAuthManager
from starlette.middleware.sessions import SessionMiddleware

from ai_client_service.dependencies import require_authenticated_client, require_authentication
from ai_client_service.models import (
    ApiKeyRequest,
    ApiKeyResponse,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionStreamChunk,
    ChatMessage,
    HealthCheckResponse,
    OAuthCallbackResponse,
)

# Export a reference so tests can patch `ai_client_service.main.CredentialStore`.
# Keep a short-lived module-level reference to avoid unused-import linting.
_CRED_STORE_TYPE = CredentialStore

# Small constants
_TUPLE_LEN = 2


def _raise_unexpected_oauth_shape(msg: str) -> None:
    """Raise a consistent ValueError for unexpected OAuth return shapes."""
    raise ValueError(msg)

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
        # Explicitly save session to ensure cookie is set
        # This is important for OAuth redirects
        logger.debug("Stored OAuth state in session: %s", state)

        oauth_manager = OAuthManager(credential_store=None)
        # Support two shapes for get_authorization_url (string or (url, state)) to
        # be compatible with different implementations and existing unit tests.
        auth_res = oauth_manager.get_authorization_url(state=state)
        if isinstance(auth_res, tuple):
            auth_url, returned_state = auth_res
        else:
            auth_url = auth_res  # type: ignore[assignment]
            returned_state = None

        # Use the state returned by oauthlib (it may modify it)
        if returned_state and returned_state != state:
            request.session["oauth_state"] = returned_state
            logger.debug("Updated OAuth state to oauthlib's state: %s", returned_state)

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
        # Note: If session cookie didn't persist, stored_state will be None
        # In that case, we rely on oauthlib's state verification in handle_callback
        stored_state = request.session.get("oauth_state")
        logger.info(
            "OAuth callback state check - received: %s, stored: %s, session keys: %s",
            state,
            stored_state,
            list(request.session.keys()),
        )
        # Verify state if we have it in session (primary check)
        # If session doesn't have it, oauthlib will verify it (secondary check)
        if stored_state and (not state or state != stored_state):
            logger.warning(
                "OAuth state mismatch - received: %s, stored: %s. Possible CSRF attack.",
                state,
                stored_state,
            )
            return OAuthCallbackResponse(
                success=False,
                message="Invalid state parameter",
                user_id=None,
            )

        # If no stored state but we have state in URL, log warning but proceed
        # oauthlib will verify the state matches what it expects
        if not stored_state and state:
            logger.warning(
                "OAuth state not found in session (session cookie may not have persisted). "
                "Relying on oauthlib state verification. Received state: %s",
                state,
            )

        # Construct the full callback URL for OAuthManager
        callback_url = str(request.url)

        oauth_manager = OAuthManager(credential_store=None)
        # Support two shapes for handle_callback: (user_id, tokens) or dict with user info.
        raw_info = oauth_manager.handle_callback(
            authorization_response=callback_url,
            state=state,
        )

        if isinstance(raw_info, tuple) and len(raw_info) == _TUPLE_LEN:
            # legacy tuple form (user_id, tokens)
            user_id, tokens = raw_info
            user_info = {"user_id": user_id}
            if isinstance(tokens, dict):
                user_info.update(tokens)
        elif isinstance(raw_info, dict):
            user_info = raw_info
        else:
            msg = "Unexpected OAuthManager.handle_callback return shape"
            _raise_unexpected_oauth_shape(msg)

        # Store user info and tokens in session
        user_id = user_info.get("user_id")
        request.session["user_id"] = user_id
        request.session["user_email"] = user_info.get("email")
        # Note: We don't store access_token/refresh_token in session as they're not needed
        # for OpenAI API calls. If needed later, we can add them. If tokens were provided
        # in the tuple form, they may be available on `user_info`.

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


@app.post("/api-keys")
def set_api_key(
    request: Request,
    api_key_request: ApiKeyRequest,
    user_id: Annotated[str, Depends(require_authentication)],
) -> ApiKeyResponse:
    """Set the OpenAI API key for the authenticated user.

    This endpoint requires the user to be authenticated via OAuth first.
    The API key will be stored in the session for use in subsequent requests.
    """
    try:
        # Store API key in session
        request.session["openai_api_key"] = api_key_request.openai_api_key
        logger.info("API key stored for user %s", user_id)

        return ApiKeyResponse(
            success=True,
            message="OpenAI API key stored successfully",
        )
    except Exception as e:
        logger.exception("Failed to store API key for user %s", user_id)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to store API key: {e!s}",
        ) from e


@app.post("/chat/completions")
def create_chat_completion(
    request: ChatCompletionRequest,
    http_request: Request,
    client: Annotated[Client, Depends(require_authenticated_client)],
) -> ChatCompletionResponse:
    """Create a chat completion.

    This endpoint requires the user to be authenticated via OAuth and have
    set their OpenAI API key.

    Args:
        request: Chat completion request data.
        client: Authenticated AI client (from dependency).
        http_request: FastAPI request object for session access.

    Returns:
        ChatCompletionResponse: Chat completion result.

    Raises:
        HTTPException: If authentication fails or the request fails.

    """
    try:
        # Get user_id from session for logging
        user_id = http_request.session.get("user_id", "unknown")

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
    client: Annotated[Client, Depends(require_authenticated_client)],
) -> Iterator[ChatCompletionStreamChunk]:
    """Create a streaming chat completion.

    This endpoint requires the user to be authenticated via OAuth and have
    set their OpenAI API key.

    Args:
        request: Chat completion request data.
        client: Authenticated AI client (from dependency).
        http_request: FastAPI request object for session access.

    Yields:
        ChatCompletionStreamChunk: Streaming chunks of the completion.

    Raises:
        HTTPException: If authentication fails or the request fails.

    """
    try:
        # Get user_id from session for logging
        user_id = http_request.session.get("user_id", "unknown")

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
