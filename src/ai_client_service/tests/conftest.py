import pytest
from fastapi.testclient import TestClient

# Import your FastAPI app from where it's defined
from ai_client_service.main import app

@pytest.fixture()
def client() -> TestClient:
    # Simple fixture; pytest will close it when the test process exits
    return TestClient(app)
