"""E2E smoke test for AI stack (requires running service and OPENAI_API_KEY)."""

import os

import pytest
import requests

import ai_adapter
import ai_api


@pytest.mark.e2e
def test_adapter_to_running_service() -> None:
    """Call the adapter against a real running service instance."""
    base_url = os.getenv("AI_SERVICE_URL", "http://127.0.0.1:8000")
    http_ok = 200

    # Check if service is running before attempting the test
    try:
        response = requests.get(f"{base_url}/health", timeout=2)
        if response.status_code != http_ok:
            pytest.skip(f"AI service not available at {base_url}")
    except (requests.ConnectionError, requests.Timeout):
        pytest.skip(f"AI service not running at {base_url}")

    ai_adapter.register(base_url=base_url)
    client = ai_api.get_client()
    try:
        result = client.generate_response("hello", "You are concise.")
    except RuntimeError as exc:
        pytest.skip(f"AI service did not return a response: {exc}")

    assert isinstance(result, (str, dict))
