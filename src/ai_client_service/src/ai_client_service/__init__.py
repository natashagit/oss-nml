"""AI Client Service with OAuth 2.0 authentication."""

from ai_client_service.dependencies import get_ai_client, set_client_factory
from ai_client_service.main import app
from ai_client_service.models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionStreamChunk,
    ChatMessage,
    ErrorResponse,
    HealthCheckResponse,
    OAuthCallbackRequest,
    OAuthCallbackResponse,
)
