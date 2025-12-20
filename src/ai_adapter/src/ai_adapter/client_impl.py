"""Adapter that calls the AI FastAPI service via generated client."""

from typing import Any, cast

from ai_service_client.api.default import generate_generate_post
from ai_service_client.models.generate_request import GenerateRequest
from ai_service_client.models.http_validation_error import HTTPValidationError

import ai_api
from ai_api import AIInterface
from ai_service_client import Client as GeneratedClient


class ServiceClient(AIInterface):
    """Client implementation that wraps the generated AI service client."""

    def __init__(self, base_url: str = "http://127.0.0.1:8000") -> None:
        """Initialize the service client with the provided base URL."""
        self.client = GeneratedClient(base_url=base_url)

    def generate_response(
        self,
        user_input: str,
        system_prompt: str,
        response_schema: dict[str, Any] | None = None,
    ) -> str | dict[str, Any]:
        """Call the service /generate endpoint and return the result."""
        body = GenerateRequest(
            user_input=user_input,
            system_prompt=system_prompt,
            response_schema=cast("Any", response_schema),
        )
        response = generate_generate_post.sync(
            client=self.client,
            body=body,
        )

        if response is None:
            msg = "No response returned from AI service"
            raise RuntimeError(msg)
        if isinstance(response, HTTPValidationError):
            msg = f"Validation error from AI service: {response}"
            raise TypeError(msg)

        result = response.result
        if isinstance(result, str):
            return result
        if hasattr(result, "to_dict"):
            return result.to_dict()
        if hasattr(result, "additional_properties"):
            return result.additional_properties
        return cast("dict[str, Any]", result)


def register(base_url: str = "http://127.0.0.1:8000") -> None:
    """Register the service adapter as the default AI client."""

    def _get_client() -> AIInterface:
        return ServiceClient(base_url=base_url)

    ai_api.get_client = _get_client
