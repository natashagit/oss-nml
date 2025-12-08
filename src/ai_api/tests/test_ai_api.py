"""Tests for ai_api interface."""

from collections.abc import Callable

import ai_api
from ai_api import AIInterface


def test_get_client_raises_when_not_registered() -> None:
    """Calling get_client without registration raises NotImplementedError."""
    original = ai_api.get_client

    def _unregistered() -> AIInterface:
        raise NotImplementedError

    setattr(ai_api, "get_client", _unregistered)
    try:
        try:
            ai_api.get_client()
        except NotImplementedError:
            assert True
        else:
            raise AssertionError("Expected NotImplementedError")
    finally:
        ai_api.get_client = original  # type: ignore[assignment]


def test_get_client_can_be_patched() -> None:
    """ai_api.get_client can be patched to return an AIInterface."""

    class DummyClient(AIInterface):
        def generate_response(self, user_input: str, system_prompt: str, response_schema=None):  # type: ignore[override]
            return "ok"

    stub: Callable[[], AIInterface] = lambda: DummyClient()
    setattr(ai_api, "get_client", stub)
    client = ai_api.get_client()
    assert isinstance(client, DummyClient)
    assert client.generate_response("hi", "be short") == "ok"
