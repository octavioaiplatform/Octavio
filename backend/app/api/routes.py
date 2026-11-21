import base64
import binascii
import asyncio
import logging
import secrets
from typing import Any

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.ai.interfaces.provider import AIProvider
from app.ai.providers.openai_realtime import OpenAIRealtimeProvider
from app.characters.manager import CharacterManager
from app.context.manager import ContextManager
from app.core.config import Settings, get_settings
from app.events.models import CLIENT_EVENT_TYPES, OctavioEvent, make_event
from app.sessions.manager import SessionManager

logger = logging.getLogger("octavio.api")
router = APIRouter()
characters = CharacterManager()
sessions: SessionManager | None = None
contexts = ContextManager()


def get_sessions(settings: Settings = Depends(get_settings)) -> SessionManager:
    global sessions
    if sessions is None or sessions.max_sessions != settings.max_sessions:
        sessions = SessionManager(settings.max_sessions)
    return sessions


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/v1/characters")
async def list_characters() -> list[dict[str, Any]]:
    return [character.model_dump(exclude={"instructions"}) for character in characters.list()]


def _is_authorized(websocket: WebSocket, settings: Settings) -> bool:
    supplied = websocket.headers.get("authorization", "")
    expected = f"Bearer {settings.access_token}"
    return secrets.compare_digest(supplied, expected)


async def _send(websocket: WebSocket, event: OctavioEvent) -> None:
    await websocket.send_text(event.model_dump_json())


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, settings: Settings = Depends(get_settings), manager: SessionManager = Depends(get_sessions)) -> None:
    if not _is_authorized(websocket, settings):
        await websocket.close(code=4401, reason="Unauthorized")
        return
    await websocket.accept()
    session_id: str | None = None
    provider: AIProvider | None = None
    provider_task: asyncio.Task[None] | None = None
    try:
        while True:
            if websocket.client_state.name != "CONNECTED":
                return
            raw = await websocket.receive_text()
            if len(raw.encode("utf-8")) > settings.max_audio_chunk_bytes * 2:
                await _send(websocket, make_event("error", session_id, code="message_too_large", message="Message exceeds limit"))
                continue
            try:
                event = OctavioEvent.model_validate_json(raw)
            except ValidationError:
                await _send(websocket, make_event("error", session_id, code="invalid_event", message="Invalid event envelope"))
                continue
            if event.type not in CLIENT_EVENT_TYPES:
                await _send(websocket, make_event("error", session_id, code="unsupported_event", message="Unsupported event type"))
                continue

            if event.type == "ping":
                await _send(websocket, make_event("pong", session_id))
                continue

            if event.type == "session.create":
                if session_id is not None:
                    await _send(websocket, make_event("error", session_id, code="session_exists", message="A session is already active on this connection"))
                    continue
                character_id = str(event.payload.get("character_id", "marcos"))
                try:
                    character = characters.get(character_id)
                    session = manager.create(character_id, player_id=_optional_str(event.payload.get("player_id")))
                except KeyError:
                    await _send(websocket, make_event("error", None, code="unknown_character", message="Character not found"))
                    continue
                except RuntimeError:
                    await _send(websocket, make_event("error", None, code="capacity_reached", message="Session capacity reached"))
                    continue
                session_id = session.id
                context = contexts.build(character.id)
                provider = OpenAIRealtimeProvider(settings, session_id, character.voice)
                await provider.connect(character.instructions, context)
                await _send(websocket, make_event("session.created", session_id, character_id=character.id))
                provider_task = asyncio.create_task(_forward_provider_events(websocket, provider))
                await _send(websocket, make_event("session.ready", session_id, character_id=character.id, provider="openai_realtime", model=settings.openai_realtime_model))
                continue

            if session_id is None:
                await _send(websocket, make_event("error", None, code="session_required", message="Create a session first"))
                continue

            current_session = manager.get(session_id)
            if event.type == "session.end":
                if provider:
                    if provider_task:
                        provider_task.cancel()
                    await provider.close()
                manager.remove(session_id)
                await _send(websocket, make_event("session.ended", session_id))
                session_id = None
                provider = None
                provider_task = None
            elif event.type == "player.context.update" and current_session:
                current_session.context = contexts.build(current_session.character_id, event.payload)
                await _send(websocket, make_event("player.context.updated", session_id))
            elif event.type == "npc.interaction.start":
                await _send(websocket, make_event("conversation.started", session_id))
            elif event.type == "npc.interaction.stop":
                await _send(websocket, make_event("npc.state.changed", session_id, state="idle"))
            elif event.type == "audio.interrupt" and provider:
                await provider.interrupt_response()
                await _send(websocket, make_event("response.completed", session_id, interrupted=True))
            elif event.type == "audio.input":
                await _handle_audio_input(websocket, event, session_id, provider, settings)
    except WebSocketDisconnect:
        pass
    except Exception:
        logger.exception("WebSocket session failed")
        try:
            await _send(websocket, make_event("error", session_id, code="internal_error", message="Internal server error"))
        except Exception:
            pass
    finally:
        if provider_task:
            provider_task.cancel()
        if provider:
            await provider.close()
        if session_id:
            manager.remove(session_id)


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)[:128]


async def _handle_audio_input(websocket: WebSocket, event: OctavioEvent, session_id: str, provider: AIProvider | None, settings: Settings) -> None:
    payload = event.payload
    audio_b64 = payload.get("audio_b64")
    sequence = payload.get("sequence")
    if not isinstance(audio_b64, str) or not isinstance(sequence, int) or sequence < 0:
        await _send(websocket, make_event("error", session_id, code="invalid_audio", message="audio_b64 and non-negative sequence are required"))
        return
    try:
        audio_bytes = base64.b64decode(audio_b64, validate=True)
    except (binascii.Error, ValueError):
        await _send(websocket, make_event("error", session_id, code="invalid_audio", message="Audio must be valid base64"))
        return
    if not audio_bytes or len(audio_bytes) > settings.max_audio_chunk_bytes:
        await _send(websocket, make_event("error", session_id, code="invalid_audio_size", message="Audio chunk is empty or too large"))
        return
    if provider is None:
        await _send(websocket, make_event("error", session_id, code="provider_unavailable", message="AI provider is not ready"))
        return
    await provider.send_audio(audio_b64, sequence)


async def _forward_provider_events(websocket: WebSocket, provider: AIProvider) -> None:
    try:
        async for event in provider.receive_events():
            await _send(websocket, event)
    except asyncio.CancelledError:
        raise
    except Exception:
        logger.exception("OpenAI Realtime event stream failed")
        try:
            await _send(websocket, make_event("error", code="provider_stream_failed", message="OpenAI Realtime connection failed"))
        except Exception:
            pass
