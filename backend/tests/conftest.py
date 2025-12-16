import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

STUBS_DIR = ROOT_DIR / "tests" / "stubs"
if str(STUBS_DIR) not in sys.path:
    sys.path.insert(0, str(STUBS_DIR))

from app.main import app
from app.runtime.memory_store import MemoryStore
from app.runtime.stats import StatsTracker


@pytest.fixture
def app_instance():
    """Reset runtime memory and return the FastAPI app for tests."""
    app.state.runtime.memory = MemoryStore()
    app.state.stats_tracker = StatsTracker()
    return app
