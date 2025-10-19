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
from mail_client_service_client.models.message_detail import MessageDetail
from mail_client_service_client.models.message_summary import MessageSummary

from mail_client_api import Client


class MessageSummaryAdapter(Message):
    """Adapter that wraps MessageSummary to implement the Message ABC interface."""

    def __init__(self, message_summary: MessageSummary) -> None:
        """Initialize the adapter with a MessageSummary instance.
        
        Args:
            message_summary: The MessageSummary instance to wrap.
        """
        self._message_summary = message_summary

    @property
    def id(self) -> str:
        """Return the unique identifier of the message."""
        return self._message_summary.id

    @property
    def from_(self) -> str:
        """Return the sender's email address."""
        return self._message_summary.from_

    @property
    def to(self) -> str:
        """Return the recipient's email address."""
        return self._message_summary.to

    @property
    def date(self) -> str:
        """Return the date the message was sent."""
        return self._message_summary.date

    @property
    def subject(self) -> str:
        """Return the subject line of the message."""
        return self._message_summary.subject

    @property
    def body(self) -> str:
        """Return the plain text content of the message.
        
        Note: MessageSummary doesn't include body, so we return an empty string.
        """
        return ""


class MessageDetailAdapter(Message):
    """Adapter that wraps MessageDetail to implement the Message ABC interface."""

    def __init__(self, message_detail: MessageDetail) -> None:
        """Initialize the adapter with a MessageDetail instance.
        
        Args:
            message_detail: The MessageDetail instance to wrap.
        """
        self._message_detail = message_detail

    @property
    def id(self) -> str:
        """Return the unique identifier of the message."""
        return self._message_detail.id

    @property
    def from_(self) -> str:
        """Return the sender's email address."""
        return self._message_detail.from_

    @property
    def to(self) -> str:
        """Return the recipient's email address."""
        return self._message_detail.to

    @property
    def date(self) -> str:
        """Return the date the message was sent."""
        return self._message_detail.date

    @property
    def subject(self) -> str:
        """Return the subject line of the message."""
        return self._message_detail.subject

    @property
    def body(self) -> str:
        """Return the plain text content of the message."""
        return self._message_detail.body


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
        if result:
            for message_summary in result:
                yield MessageSummaryAdapter(message_summary)
        else:
            return iter([])

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
            msg = f"Message {message_id} not found"
            raise ValueError(msg)
        return MessageDetailAdapter(result)

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

