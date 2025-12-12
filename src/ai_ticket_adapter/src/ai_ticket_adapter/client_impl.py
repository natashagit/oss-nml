"""Adapter wrapping the generated AI ticket service client."""

from __future__ import annotations

from ai_ticket_service_client.api.default.command_command_post import sync
from ai_ticket_service_client.models import CommandRequest, CommandResponse
from ai_ticket_service_client.types import UNSET

from ai_ticket_service_client import Client


class TicketOrchestrationAdapter:
    """Thin wrapper around the generated AI ticket service client."""

    def __init__(self, base_url: str = "http://127.0.0.1:8000") -> None:
        """Initialize the adapter with a target base URL."""
        self._client = Client(base_url=base_url)

    def command(
        self,
        user_input: str,
        system_prompt: str | None = None,
    ) -> CommandResponse | None:
        """Call the /command endpoint and return the parsed response or None on validation errors."""
        request = CommandRequest(
            user_input=user_input,
            system_prompt=system_prompt if system_prompt is not None else UNSET,
        )
        response = sync(client=self._client, body=request)
        if isinstance(response, CommandResponse):
            return response
        return None

    def raw_response(
        self,
        user_input: str,
        system_prompt: str | None = None,
    ) -> CommandResponse:
        """Call /command and raise if no response is parsed."""
        response = self.command(user_input=user_input, system_prompt=system_prompt)
        if response is None:
            msg = "No response returned from AI ticket service"
            raise RuntimeError(msg)
        return response

    @property
    def base_url(self) -> str:
        """Return the configured base URL."""
        return self._client._base_url  # noqa: SLF001
