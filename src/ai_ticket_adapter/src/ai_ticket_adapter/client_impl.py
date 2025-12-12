"""Adapter wrapping the generated AI ticket service client."""

from __future__ import annotations

from typing import Optional

from ai_ticket_service_client import Client
from ai_ticket_service_client.api.default.command_command_post import sync
from ai_ticket_service_client.models import CommandRequest, CommandResponse
from ai_ticket_service_client.types import UNSET


class TicketOrchestrationAdapter:
    """Thin wrapper around the generated AI ticket service client."""

    def __init__(self, base_url: str = "http://127.0.0.1:8000") -> None:
        self._client = Client(base_url=base_url)

    def command(
        self,
        user_input: str,
        system_prompt: str | None = None,
    ) -> Optional[CommandResponse]:
        """Call the /command endpoint and return the parsed response or None on validation errors."""
        request = CommandRequest(
            user_input=user_input,
            system_prompt=system_prompt if system_prompt is not None else UNSET,
        )
        return sync(client=self._client, body=request)

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
        return self._client.base_url
