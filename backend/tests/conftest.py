import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import app
from app.api.routes import get_sessions
from app.sessions.manager import SessionManager


class TestRealtimeProvider:
    def __init__(self, settings, session_id, voice="marin"):
        self.session_id = session_id

    async def connect(self, character_instructions, context):
        pass

    async def send_audio(self, audio_b64, sequence):
        pass

    async def interrupt_response(self):
        pass

    async def receive_events(self):
        if False:
            yield None

    async def close(self):
        pass


@pytest.fixture
def client(monkeypatch):
    import app.api.routes as routes

    monkeypatch.setattr(routes, "OpenAIRealtimeProvider", TestRealtimeProvider)
    settings = Settings(OCTAVIO_ENV="test", OCTAVIO_ACCESS_TOKEN="test-token", OCTAVIO_MAX_SESSIONS=2)
    manager = SessionManager(max_sessions=2)
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_sessions] = lambda: manager
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
