import pytest
from mail_client_service_client.models import (
    MessageSummary,
    MessageDetail,
)
from mail_client_service_client.api.default import (
    get_messages_messages_get,
    get_message_messages_message_id_get,
    delete_message_messages_message_id_delete,
    mark_message_as_read_messages_message_id_mark_as_read_post,
)

# Import the ServiceClient from mail_client_adapter
from mail_client_adapter.client_impl import ServiceClient


def test_get_messages_calls_generated_client(monkeypatch):
    mock_resp = [
        MessageSummary(
            id="1",
            from_="a@test.com",
            to=["b@test.com"],
            date="2024-01-01",
            subject="Hi",
        )
    ]
    monkeypatch.setattr(
        get_messages_messages_get, "sync",
        lambda client, max_results: mock_resp
    )

    svc = ServiceClient()
    resp = svc.get_messages(max_results=5)

    assert isinstance(resp, list)
    assert isinstance(resp[0], MessageSummary)
    assert resp[0].subject == "Hi"


def test_get_message_calls_generated_client(monkeypatch):
    mock_resp = MessageDetail(
        id="123",
        from_="a@test.com",
        to=["b@test.com"],
        date="2024-01-01",
        subject="Hello",
        body="This is a test message",
    )
    monkeypatch.setattr(
        get_message_messages_message_id_get, "sync",
        lambda client, message_id: mock_resp
    )

    svc = ServiceClient()
    resp = svc.get_message("123")

    assert isinstance(resp, MessageDetail)
    assert resp.id == "123"
    assert resp.subject == "Hello"


def test_delete_message_returns_true_on_ok(monkeypatch):
    class FakeResp:
        status = "ok"

    monkeypatch.setattr(
        delete_message_messages_message_id_delete, "sync",
        lambda client, message_id: FakeResp()
    )

    svc = ServiceClient()
    assert svc.delete_message("123") is True


def test_delete_message_returns_false_on_fail(monkeypatch):
    class FakeResp:
        status = "error"

    monkeypatch.setattr(
        delete_message_messages_message_id_delete, "sync",
        lambda client, message_id: FakeResp()
    )

    svc = ServiceClient()
    assert svc.delete_message("123") is False


def test_mark_as_read_returns_true_on_ok(monkeypatch):
    class FakeResp:
        status = "ok"

    monkeypatch.setattr(
        mark_message_as_read_messages_message_id_mark_as_read_post, "sync",
        lambda client, message_id: FakeResp()
    )

    svc = ServiceClient()
    assert svc.mark_as_read("123") is True


def test_mark_as_read_returns_false_on_fail(monkeypatch):
    class FakeResp:
        status = "error"

    monkeypatch.setattr(
        mark_message_as_read_messages_message_id_mark_as_read_post, "sync",
        lambda client, message_id: FakeResp()
    )

    svc = ServiceClient()
    assert svc.mark_as_read("123") is False
