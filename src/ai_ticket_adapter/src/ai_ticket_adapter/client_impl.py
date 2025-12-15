"""Adapter wrapping the generated AI ticket service client."""

from __future__ import annotations

import logging

import httpx

from ai_ticket_service_client.api.default.command_command_post import sync
from ai_ticket_service_client.models import CommandRequest, CommandResponse
from ai_ticket_service_client.types import UNSET

from ai_ticket_service_client import Client

logger = logging.getLogger(__name__)


class TicketOrchestrationAdapter:
    """Thin wrapper around the generated AI ticket service client."""

    def __init__(self, base_url: str = "http://127.0.0.1:8000") -> None:
        """Initialize the adapter with a target base URL."""
        self._client = Client(base_url=base_url)

    def command(
        self,
        user_input: str,
        system_prompt: str | None = None,
        backend: str | None = None,
    ) -> CommandResponse | None:
        """Call the /command endpoint and return the parsed response or None on validation errors.

        Raises:
            httpx.HTTPError: For network failures, connection errors, timeouts, or HTTP errors
            RuntimeError: For unexpected errors during the request

        """
        request = CommandRequest(
            user_input=user_input,
            system_prompt=system_prompt if system_prompt is not None else UNSET,
            backend=backend if backend is not None else UNSET,
        )
        try:
            response = sync(client=self._client, body=request)
        except httpx.TimeoutException as exc:
            logger.error("Request to %s timed out: %s", self._client._base_url, exc)  # noqa: SLF001
            raise
        except httpx.ConnectError as exc:
            logger.error("Failed to connect to %s: %s", self._client._base_url, exc)  # noqa: SLF001
            raise
        except httpx.HTTPStatusError as exc:
            logger.error(
                "HTTP error %s from %s: %s",
                exc.response.status_code,
                self._client._base_url,  # noqa: SLF001
                exc.response.text,
            )
            raise
        except httpx.HTTPError as exc:
            logger.error("Network/HTTP error when calling %s: %s", self._client._base_url, exc)  # noqa: SLF001
            raise
        except Exception as exc:
            logger.exception("Unexpected error when calling AI ticket service at %s", self._client._base_url)  # noqa: SLF001
            msg = f"Unexpected error calling AI ticket service: {exc!s}"
            raise RuntimeError(msg) from exc

        if isinstance(response, CommandResponse):
            return response
        return None

    def raw_response(
        self,
        user_input: str,
        system_prompt: str | None = None,
        backend: str | None = None,
    ) -> CommandResponse:
        """Call /command and raise if no response is parsed.

        Raises:
            httpx.HTTPError: For network failures, connection errors, timeouts, or HTTP errors
            RuntimeError: If no response is returned or for unexpected errors during the request

        """
        response = self.command(user_input=user_input, system_prompt=system_prompt, backend=backend)
        if response is None:
            msg = "No response returned from AI ticket service"
            raise RuntimeError(msg)
        return response

    @property
    def base_url(self) -> str:
        """Return the configured base URL."""
        return self._client._base_url  # noqa: SLF001
