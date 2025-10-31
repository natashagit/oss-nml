"""Test fixtures for the ai_client_service package tests."""

import importlib
import sys
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]  # .../project/src
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_ai_mod = importlib.import_module("ai_client_service.main")
app = _ai_mod.app  # use the real app under test

# Try to import the dependencies module if it exists
try:
    import ai_client_service.dependencies as deps  # type: ignore[import]
except ImportError:
    deps = None  # type: ignore[assignment]


class _FakeCredentialStore:
    """No-op credential store to avoid real DB/network calls in tests."""

    def save_tokens(self, _user_id: str, _tokens: dict[str, str]) -> None:
        return None

    def store_google_tokens(self, _user_id: str, _tokens: dict[str, str]) -> None:
        return None


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """TestClient with safe dependency overrides.

    - Override `get_credential_store` (wherever defined) to avoid DB.
    - `follow_redirects=False` so tests can assert 307 on `/oauth/authorize`.
    """
    # Override get_credential_store from ai_client_service.dependencies (if present)
    if deps and hasattr(deps, "get_credential_store"):
        app.dependency_overrides[deps.get_credential_store] = lambda: _FakeCredentialStore()

    # Also override if get_credential_store is defined directly in main
    try:
        _main = importlib.import_module("ai_client_service.main")

        if hasattr(_main, "get_credential_store"):
            app.dependency_overrides[_main.get_credential_store] = lambda: _FakeCredentialStore()
    except ImportError:
        # If main has unexpected import-time side effects in some environments,
        # we prefer tests to continue rather than crash during fixture setup.
        pass

    test_client = TestClient(app, follow_redirects=False)
    try:
        yield test_client
    finally:
        app.dependency_overrides.clear()
