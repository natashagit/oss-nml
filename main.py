"""Entry point for demonstrating the AI service stack."""

import logging
import os

import ai_adapter
import ai_api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run a small AI demo against the running AI service."""
    base_url = os.getenv("AI_SERVICE_URL", "http://127.0.0.1:8000")

    # Wire the AI adapter to point at the service
    ai_adapter.register(base_url=base_url)
    client = ai_api.get_client()

    logger.info("Calling AI service at %s", base_url)

    # Conversational call
    text_response = client.generate_response("Say hello in 3 words.", "You are concise.")
    print("Conversational response:", text_response)  # noqa: T201

    # Structured call using a simple schema
    schema = {
        "name": "ticket_command",
        "description": "Extract intent and title from a ticket request",
        "schema": {
            "type": "object",
            "properties": {
                "intent": {"type": "string"},
                "title": {"type": "string"},
            },
            "required": ["intent", "title"],
            "additionalProperties": False,
        },
    }
    structured = client.generate_response(
        "Create a ticket to fix login redirect.",
        "Extract intent and title fields.",
        response_schema=schema,
    )
    print("Structured response:", structured)  # noqa: T201

    print("AI demo complete.")  # noqa: T201


if __name__ == "__main__":
    main()
