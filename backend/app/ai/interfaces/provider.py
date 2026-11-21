from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from app.events.models import OctavioEvent


class AIProvider(ABC):
    """Provider boundary; game/session code must not depend on vendor events."""

    @abstractmethod
    async def connect(self, character_instructions: str, context: dict[str, str]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def send_audio(self, audio_b64: str, sequence: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def interrupt_response(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def receive_events(self) -> AsyncIterator[OctavioEvent]:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError
