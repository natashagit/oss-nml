"""AI Client Service with OAuth 2.0 authentication."""

from ai_client_service.dependencies import get_ai_client as get_ai_client
from ai_client_service.dependencies import set_client_factory as set_client_factory
from ai_client_service.main import app as app
from ai_client_service.models import ChatCompletionRequest as ChatCompletionRequest
from ai_client_service.models import ChatCompletionResponse as ChatCompletionResponse
from ai_client_service.models import (
    ChatCompletionStreamChunk as ChatCompletionStreamChunk,
)
from ai_client_service.models import ChatMessage as ChatMessage
from ai_client_service.models import ErrorResponse as ErrorResponse
from ai_client_service.models import HealthCheckResponse as HealthCheckResponse
from ai_client_service.models import OAuthCallbackRequest as OAuthCallbackRequest
from ai_client_service.models import OAuthCallbackResponse as OAuthCallbackResponse

__all__ = [
    "ChatCompletionRequest",
    "ChatCompletionResponse",
    "ChatCompletionStreamChunk",
    "ChatMessage",
    "ErrorResponse",
    "HealthCheckResponse",
    "OAuthCallbackRequest",
    "OAuthCallbackResponse",
    "app",
    "get_ai_client",
    "set_client_factory",
]
