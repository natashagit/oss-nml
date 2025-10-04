"""Service client implementation for mail client adapter."""

# Import generated API calls from the `default` subpackage
from collections.abc import Iterator

from mail_client_api.message import Message
from mail_client_service_client.api.default import (
    delete_message_messages_message_id_delete,
    get_message_messages_message_id_get,
    get_messages_messages_get,
    mark_message_as_read_messages_message_id_mark_as_read_post,
)
from mail_client_service_client.client import Client as GeneratedClient

from mail_client_api import Client


class ServiceClient(Client):
    """Client implementation that wraps the generated mail client service API."""

    def __init__(self, base_url: str = "http://127.0.0.1:8000") -> None:
        """Initialize the service client.

        Args:
            base_url: The base URL of the mail client service.

        """
        self.client = GeneratedClient(base_url=base_url)

    def get_messages(self, max_results: int = 10) -> Iterator[Message]:
        """Retrieve a list of messages.

        Args:
            max_results: Maximum number of messages to retrieve.

        Returns:
            Iterator of message objects.

        """
        result = get_messages_messages_get.sync(client=self.client, max_results=max_results)
        return iter(result) if result else iter([])

    def get_message(self, message_id: str) -> Message:
        """Retrieve a single message by ID.

        Args:
            message_id: The unique identifier of the message.

        Returns:
            The message object.

        Raises:
            ValueError: If the message could not be retrieved.

        """
        result = get_message_messages_message_id_get.sync(client=self.client, message_id=message_id)
        if result is None:
            raise ValueError(f"Message {message_id} not found")
        return result

    def delete_message(self, message_id: str) -> bool:
        """Delete a message by ID.

        Args:
            message_id: The unique identifier of the message.

        Returns:
            True if deletion was successful, False otherwise.

        """
        resp = delete_message_messages_message_id_delete.sync(
            client=self.client, message_id=message_id,
        )
        return getattr(resp, "status", None) == "ok"

    def mark_as_read(self, message_id: str) -> bool:
        """Mark a message as read.

        Args:
            message_id: The unique identifier of the message.

        Returns:
            True if marking as read was successful, False otherwise.

        """
        resp = mark_message_as_read_messages_message_id_mark_as_read_post.sync(
            client=self.client, message_id=message_id,
        )
        return getattr(resp, "status", None) == "ok"

    def get_client(self) -> GeneratedClient:
        """Get the underlying generated client.

        Returns:
            The generated client instance.

        """
        return self.client

