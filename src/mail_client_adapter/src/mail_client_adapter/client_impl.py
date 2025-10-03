from mail_client_api import Client, Message
from mail_client_service_client.client import Client as GeneratedClient

# Import generated API calls from the `default` subpackage
from mail_client_service_client.api.default import (
    delete_message_messages_message_id_delete,
    get_message_messages_message_id_get,
    get_messages_messages_get,
    mark_message_as_read_messages_message_id_mark_as_read_post,
)


class ServiceClient(Client):

    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.client = GeneratedClient(base_url=base_url)

    def get_messages(self, max_results: int = 10):
        return get_messages_messages_get.sync(client=self.client, max_results=max_results)

    def get_message(self, message_id: str):
        return get_message_messages_message_id_get.sync(client=self.client, message_id=message_id)

    def delete_message(self, message_id: str) -> bool:
        resp = delete_message_messages_message_id_delete.sync(
            client=self.client, message_id=message_id
        )
        return getattr(resp, "status", None) == "ok"

    def mark_as_read(self, message_id: str) -> bool:
        resp = mark_message_as_read_messages_message_id_mark_as_read_post.sync(
            client=self.client, message_id=message_id
        )
        return getattr(resp, "status", None) == "ok"
    
    def get_client(self):
        return self.client

