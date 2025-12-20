"""Pydantic models for AI service."""

from typing import Any

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Request payload for generate endpoint."""

    user_input: str = Field(..., description="The text provided by the chat user.")
    system_prompt: str = Field(..., description="Instructional system prompt.")
    response_schema: dict[str, Any] | None = Field(
        default=None,
        description="Optional JSON schema dict for structured responses.",
    )


class GenerateResponse(BaseModel):
    """Response payload for generate endpoint."""

    result: str | dict[str, Any] = Field(..., description="String response or structured dict.")


class HealthCheckResponse(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
