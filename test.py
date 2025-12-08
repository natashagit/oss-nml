"""Simple smoke tests for local impl and service adapter.

Run with:
  # local OpenAI implementation
  uv run python test.py local

  # adapter against running service (expects service at http://127.0.0.1:8000)
  uv run python test.py adapter

Requires OPENAI_API_KEY in the environment for the local impl; the adapter
relies on the service having its provider configured.
"""

import os
import sys

import ai_api


def test_local() -> None:
    """Smoke test using the local OpenAI implementation."""
    import openai_impl

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY not set; skipping local impl smoke test.")
        return

    openai_impl.register(api_key=api_key)
    client = ai_api.get_client("smoke-local")
    result = client.generate_response("hello", "You are concise.")
    print("[local] response:", result)


def test_adapter() -> None:
    """Smoke test using the service adapter (service must be running)."""
    import ai_adapter

    ai_adapter.register(base_url="http://127.0.0.1:8000")
    client = ai_api.get_client("smoke-adapter")
    result = client.generate_response("hello how are you?", "You are assistant")
    print("[adapter] response:", result)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "local"
    if mode == "local":
        test_local()
    elif mode == "adapter":
        test_adapter()
    else:
        print("Usage: python test.py [local|adapter]")
