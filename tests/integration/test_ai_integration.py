"""Integration test: adapter -> service -> mocked AI client."""

from typing import Any
from unittest.mock import patch

from ai_service.main import app
from fastapi.testclient import TestClient

import ai_adapter
import ai_api
from ai_api import AIInterface


class DummyAIClient(AIInterface):
    """Simple AI client that returns a fixed response."""

    def generate_response(
        self,
        user_input: str,
        system_prompt: str,
        response_schema: dict[str, Any] | None = None,
    ) -> str | dict[str, Any]:
        """Return an echo-like structured response."""
        return {"echo": user_input, "prompt": system_prompt}


def test_adapter_calls_service_with_mocked_impl() -> None:
    """End-to-end through adapter into service using ASGI transport and mocked get_client."""
    tc = TestClient(app)

    class FakeHTTPXClient:
        def request(
            self,
            method: str,
            url: str,
            data: Any = None,
            headers: dict[str, str] | None = None,
            json: Any | None = None,
            **_: object,
        ) -> Any:
            if json is not None:
                return tc.request(method, url, json=json, headers=headers)
            if headers and headers.get("Content-Type") == "application/json" and data:
                import json as json_module

                return tc.request(method, url, json=json_module.loads(data), headers=headers)
            return tc.request(method, url, data=data, headers=headers)

    with (
        patch("ai_service.main.get_client", return_value=DummyAIClient()),
        patch("ai_service_client.client.Client.get_httpx_client", return_value=FakeHTTPXClient()),
    ):
        ai_adapter.register(base_url="http://testserver")
        client = ai_api.get_client()
        result = client.generate_response("hello", "You are concise.")
    # Normalize possible model wrappers
    if hasattr(result, "to_dict"):
        result_dict = result.to_dict()  # type: ignore[assignment]
        result = result_dict.get("result", result_dict)
    elif hasattr(result, "result"):
        result = result.result  # type: ignore[assignment]
    assert result == {"echo": "hello", "prompt": "You are concise."}
