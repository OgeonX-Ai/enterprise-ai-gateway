import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.runtime.memory_store import MemoryStore


@pytest.fixture
def client():
    # Reset runtime memory between tests to keep isolation
    app.state.runtime.memory = MemoryStore()
    return TestClient(app)
