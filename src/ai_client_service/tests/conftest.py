# src/ai_client_service/tests/conftest.py
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure /src is importable (local + CI)
ROOT = Path(__file__).resolve().parents[2]  # .../project/src
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ai_client_service.main import app  # use the real app under test

# Try to import the dependencies module if it exists
try:
    import ai_client_service.dependencies as deps  # type: ignore
except Exception:  # pragma: no cover
    deps = None  # type: ignore


class _FakeCredentialStore:
    """No-op credential store to avoid real DB/network calls in tests."""
    def save_tokens(self, user_id, tokens):
        return None

    def store_google_tokens(self, user_id, tokens):
        return None


@pytest.fixture
def client():
    """
    TestClient with safe dependency overrides:
    - Override get_credential_store (wherever defined) to avoid DB.
    - follow_redirects=False so tests can assert 307 on /oauth/authorize.
    """
    # Override get_credential_store from ai_client_service.dependencies (if present)
    if deps and hasattr(deps, "get_credential_store"):
        app.dependency_overrides[deps.get_credential_store] = lambda: _FakeCredentialStore()

    # Also override if get_credential_store is defined directly in main
    try:
        from ai_client_service import main as _main  # lazy import to avoid circulars
        if hasattr(_main, "get_credential_store"):
            app.dependency_overrides[_main.get_credential_store] = lambda: _FakeCredentialStore()
    except Exception:
        pass

    test_client = TestClient(app, follow_redirects=False)
    try:
        yield test_client
    finally:
        app.dependency_overrides.clear()
