from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class OctavioEvent(BaseModel):
    """Versionable event envelope shared by game clients and the backend."""

    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    type: str
    payload: dict[str, Any] = Field(default_factory=dict)


CLIENT_EVENT_TYPES = {
    "session.create",
    "session.end",
    "npc.interaction.start",
    "npc.interaction.stop",
    "audio.input",
    "audio.interrupt",
    "player.context.update",
    "ping",
}


def make_event(event_type: str, session_id: str | None = None, **payload: Any) -> OctavioEvent:
    return OctavioEvent(type=event_type, session_id=session_id, payload=payload)
