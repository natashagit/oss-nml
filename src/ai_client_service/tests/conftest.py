import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure the workspace 'src' is importable in CI/local
ROOT = Path(__file__).resolve().parents[2]  # .../project/src
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mail_client_service.main import app  # adjust if your app lives elsewhere

@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
