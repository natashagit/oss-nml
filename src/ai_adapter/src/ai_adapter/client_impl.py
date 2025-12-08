"""Adapter that calls the AI FastAPI service via generated client."""

from typing import Any

import ai_api
from ai_api import AIInterface
from ai_service_client import Client as GeneratedClient
from ai_service_client.api.default import generate_generate_post
from ai_service_client.models.generate_request import GenerateRequest


class ServiceClient(AIInterface):
    """Client implementation that wraps the generated AI service client."""

    def __init__(self, base_url: str = "http://127.0.0.1:8000") -> None:
        self.client = GeneratedClient(base_url=base_url)

    def generate_response(
        self,
        user_input: str,
        system_prompt: str,
        response_schema: dict[str, Any] | None = None,
    ) -> str | dict[str, Any]:
        body = GenerateRequest(
            user_input=user_input,
            system_prompt=system_prompt,
            response_schema=response_schema,
        )
        response = generate_generate_post.sync(
            client=self.client,
            body=body,
        )

        if response is None:
            raise RuntimeError("No response returned from AI service")

        return response.result


def register(base_url: str = "http://127.0.0.1:8000") -> None:
    """Register the service adapter as the default AI client."""

    def _get_client(user_id: str) -> AIInterface:  # noqa: ARG001 - parity with ai_api.get_client
        return ServiceClient(base_url=base_url)

    ai_api.get_client = _get_client  # type: ignore[assignment]
