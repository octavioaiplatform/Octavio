import base64

import pytest
from starlette.websockets import WebSocketDisconnect


def event(event_type, payload=None):
    return {"event_id": "test-event", "session_id": None, "type": event_type, "payload": payload or {}}


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_character_list(client):
    response = client.get("/v1/characters")
    assert response.status_code == 200
    assert response.json()[0]["id"] == "marcos"
    assert "instructions" not in response.json()[0]


def test_websocket_session_lifecycle(client):
    with client.websocket_connect("/ws", headers={"Authorization": "Bearer test-token"}) as websocket:
        websocket.send_json(event("session.create", {"character_id": "marcos", "player_id": "player-1"}))
        created = websocket.receive_json()
        ready = websocket.receive_json()
        assert created["type"] == "session.created"
        assert created["session_id"]
        assert ready["type"] == "session.ready"
        assert ready["payload"]["provider"] == "mock"

        websocket.send_json(event("npc.interaction.start"))
        assert websocket.receive_json()["type"] == "conversation.started"

        audio = base64.b64encode(b"mock-audio").decode("ascii")
        websocket.send_json(event("audio.input", {"audio_b64": audio, "sequence": 0}))
        speech = websocket.receive_json()
        assert speech["type"] == "speech.detected"
        assert speech["payload"]["transport"] == "mock"

        websocket.send_json(event("session.end"))
        assert websocket.receive_json()["type"] == "session.ended"


def test_websocket_rejects_invalid_audio(client):
    with client.websocket_connect("/ws", headers={"Authorization": "Bearer test-token"}) as websocket:
        websocket.send_json(event("session.create", {"character_id": "marcos"}))
        websocket.receive_json()
        websocket.receive_json()
        websocket.send_json(event("audio.input", {"audio_b64": "!!!", "sequence": 0}))
        error = websocket.receive_json()
        assert error["type"] == "error"
        assert error["payload"]["code"] == "invalid_audio"


def test_websocket_requires_authentication(client):
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect("/ws"):
            raise AssertionError("Unauthenticated connection unexpectedly opened")
    assert exc.value.code == 4401
    assert exc.value.reason == "Unauthorized"
