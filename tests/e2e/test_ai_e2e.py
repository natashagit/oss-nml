"""E2E smoke test for AI stack (requires running service and OPENAI_API_KEY)."""

import os

import ai_adapter
import ai_api


def test_adapter_to_running_service() -> None:
    """Call the adapter against a real running service instance."""
    base_url = os.getenv("AI_SERVICE_URL", "http://127.0.0.1:8000")
    ai_adapter.register(base_url=base_url)
    client = ai_api.get_client()
    result = client.generate_response("hello", "You are concise.")
    # We don't assert on exact content since it depends on live model, just ensure we got a response.
    assert isinstance(result, (str, dict))
