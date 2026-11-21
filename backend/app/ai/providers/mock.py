from collections.abc import AsyncIterator

from app.ai.interfaces.provider import AIProvider
from app.events.models import OctavioEvent, make_event


class MockAIProvider(AIProvider):
    """Deterministic transport mock; it does not transcribe or synthesize audio."""

    def __init__(self) -> None:
        self._events: list[OctavioEvent] = []
        self._connected = False

    async def connect(self, character_instructions: str, context: dict[str, str]) -> None:
        self._connected = True
        self._events.append(make_event("session.ready", character_id=context.get("character_id", "marcos")))

    async def send_audio(self, audio_b64: str, sequence: int) -> None:
        if not self._connected:
            raise RuntimeError("AI provider is not connected")
        # The mock acknowledges transport only. It deliberately emits no fabricated transcript/audio.

    async def interrupt_response(self) -> None:
        self._events.append(make_event("response.completed", interrupted=True))

    async def receive_events(self) -> AsyncIterator[OctavioEvent]:
        while self._events:
            yield self._events.pop(0)

    async def close(self) -> None:
        self._connected = False
