import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import app
from app.api.routes import get_sessions
from app.sessions.manager import SessionManager


@pytest.fixture
def client():
    settings = Settings(OCTAVIO_ENV="test", OCTAVIO_ACCESS_TOKEN="test-token", OCTAVIO_MAX_SESSIONS=2)
    manager = SessionManager(max_sessions=2)
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_sessions] = lambda: manager
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
