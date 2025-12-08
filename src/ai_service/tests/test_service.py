"""Unit tests for AI FastAPI service."""

from unittest.mock import Mock, patch

from ai_service.main import app
from fastapi.testclient import TestClient

HTTP_OK = 200
HTTP_SERVER_ERROR = 500


def test_health() -> None:
    """Health check returns expected payload."""
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == HTTP_OK
    body = resp.json()
    assert body["status"] == "healthy"


def test_generate_success() -> None:
    """Generate endpoint returns result when client succeeds."""
    mock_ai_client = Mock()
    mock_ai_client.generate_response.return_value = "ok"

    with patch("ai_service.main.get_client", return_value=mock_ai_client):
        client = TestClient(app)
        resp = client.post(
            "/generate",
            json={"user_input": "hi", "system_prompt": "be short"},
        )

    assert resp.status_code == HTTP_OK
    assert resp.json()["result"] == "ok"


def test_generate_failure_returns_500() -> None:
    """Generate endpoint surfaces errors as 500."""
    mock_ai_client = Mock()
    mock_ai_client.generate_response.side_effect = RuntimeError("boom")

    with patch("ai_service.main.get_client", return_value=mock_ai_client):
        client = TestClient(app)
        resp = client.post(
            "/generate",
            json={"user_input": "hi", "system_prompt": "be short"},
        )

    assert resp.status_code == HTTP_SERVER_ERROR
    assert "Generation failed" in resp.json()["detail"]
