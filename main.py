"""Main module for demonstrating the AI client."""

# ta-assignment/main.py

import contextlib
import logging

import ai_client_adapter  # noqa: F401
import ai_client_api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """Initialize the client and demonstrate all AI client methods."""
    # Now, get_client() returns an OpenAIClient instance...
    user_id = "demo_user"
    
    try:
        client = ai_client_api.get_client(user_id)
        logger.info("Successfully initialized AI client")
    except Exception as e:
        logger.error("Failed to initialize AI client: %s", e)
        logger.error("Exception type: %s", type(e).__name__)
        import traceback
        logger.error("Traceback: %s", traceback.format_exc())
        logger.info("Make sure you have valid credentials stored for user: %s", user_id)
        return

    # Test 1: Chat completion (existing functionality)
    messages = [
        {"role": "user", "content": "Hello! Can you tell me a short joke?"}
    ]
    
    try:
        logger.info("Testing chat completion...")
        response = client.chat_completion(messages)
        logger.info("Chat completion response: %s", response["message"]["content"])
    except Exception as e:
        logger.error("Chat completion failed: %s", e)

    # Test 2: Streaming chat completion
    streaming_messages = [
        {"role": "user", "content": "Tell me a short story about a robot."}
    ]
    
    try:
        logger.info("Testing streaming chat completion...")
        print("Streaming response: ", end="", flush=True)
        for chunk in client.chat_completion_stream(streaming_messages):
            if chunk.get("content"):
                print(chunk["content"], end="", flush=True)
        print()  # New line after streaming
    except Exception as e:
        logger.error("Streaming chat completion failed: %s", e)

    # Test 3: Different model and parameters
    advanced_messages = [
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": "Explain what dependency injection is in one sentence."}
    ]
    
    try:
        logger.info("Testing advanced chat completion with different parameters...")
        response = client.chat_completion(
            messages=advanced_messages,
            model="gpt-3.5-turbo",
            temperature=0.3,
            max_tokens=100
        )
        logger.info("Advanced completion response: %s", response["message"]["content"])
    except Exception as e:
        logger.error("Advanced chat completion failed: %s", e)

    print("AI Client Demo complete.")  # noqa: T201


if __name__ == "__main__":
    main()
