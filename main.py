"""Main module for demonstrating the AI client via the service adapter."""

import contextlib
import logging
import traceback

import ai_client_adapter  # noqa: F401  (auto-registers service adapter)
import ai_client_api
from ai_client_api.models import ChatMessage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """Initialize the client and demonstrate all AI client methods."""
    # Now, get_client() returns a concrete OpenAIClient instance via auto-registration
    user_id = "demo_user"

    try:
        client = ai_client_api.get_client(user_id)
        logger.info("Successfully initialized AI client")
    except Exception as e:
        logger.exception("Failed to initialize AI client")
        logger.exception("Exception type: %s", type(e).__name__)
        logger.exception("Traceback: %s", traceback.format_exc())
        logger.info("Make sure you have valid credentials stored for user: %s", user_id)
        return

    # Test 1: Chat completion
    messages = [ChatMessage(role="user", content="hello, how are you?")]
    logger.info("Testing chat completion...")
    with contextlib.suppress(Exception):
        resp = client.chat_completion(messages, model="gpt-3.5-turbo-0125")
        logger.info("%s", resp.message.content)

    # Test 2: Streaming chat completion
    streaming_messages = [ChatMessage(role="user", content="Write two short sentences about a flight.")]
    logger.info("Testing streaming chat completion...")
    with contextlib.suppress(Exception):
        for chunk in client.chat_completion_stream(streaming_messages, model="gpt-3.5-turbo-0125"):
            if chunk.content:
                pass

    # Test 3: Different model and parameters
    advanced_messages = [
        ChatMessage(role="system", content="You are a helpful coding assistant."),
        ChatMessage(role="user", content="Explain what dependency injection is in one sentence."),
    ]
    logger.info("Testing advanced chat completion...")
    with contextlib.suppress(Exception):
        resp = client.chat_completion(
            messages=advanced_messages,
            model="gpt-3.5-turbo-0125",
            temperature=0.3,
            max_tokens=100,
        )
        logger.info("%s", resp.message.content)

    print("Demo complete.")  # noqa: T201


if __name__ == "__main__":
    main()
