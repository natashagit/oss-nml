"""Pydantic models for AI client service request/response serialization."""


from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single message in a chat conversation."""

    role: str = Field(..., description="The role of the message sender (system, user, assistant)")
    content: str = Field(..., description="The content of the message")


class ChatCompletionRequest(BaseModel):
    """Request model for chat completion."""

    messages: list[ChatMessage] = Field(..., description="List of messages in the conversation")
    model: str = Field(default="gpt-3.5-turbo", description="The AI model to use")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int | None = Field(default=None, ge=1, description="Maximum tokens to generate")


class ChatCompletionResponse(BaseModel):
    """Response model for chat completion."""

    message: ChatMessage = Field(..., description="The generated message")
    model: str = Field(..., description="The model used for generation")
    usage: dict[str, int] = Field(..., description="Token usage information")
    finish_reason: str | None = Field(None, description="Reason for completion")


class ChatCompletionStreamChunk(BaseModel):
    """A single chunk in a streaming chat completion."""

    content: str = Field(..., description="The content delta for this chunk")
    finish_reason: str | None = Field(
        None,
        description="Reason for stopping (present in final chunk)",
    )
    model: str = Field(..., description="The model being used")


class OAuthCallbackRequest(BaseModel):
    """Request model for OAuth callback."""

    code: str = Field(..., description="Authorization code from OAuth provider")
    state: str | None = Field(None, description="State parameter for CSRF protection")


class OAuthCallbackResponse(BaseModel):
    """Response model for OAuth callback."""

    success: bool = Field(..., description="Whether the OAuth flow was successful")
    message: str = Field(..., description="Status message")
    user_id: str | None = Field(None, description="User ID if successful")


class HealthCheckResponse(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error type")
    detail: str = Field(..., description="Error details")
    status_code: int = Field(..., description="HTTP status code")
