from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class Session:
    id: str = field(default_factory=lambda: str(uuid4()))
    player_id: str | None = None
    character_id: str = "marcos"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    context: dict[str, str] = field(default_factory=dict)


class SessionManager:
    def __init__(self, max_sessions: int = 100) -> None:
        self._sessions: dict[str, Session] = {}
        self._max_sessions = max_sessions

    def create(self, character_id: str, player_id: str | None = None) -> Session:
        if len(self._sessions) >= self._max_sessions:
            raise RuntimeError("Maximum concurrent sessions reached")
        session = Session(player_id=player_id, character_id=character_id)
        self._sessions[session.id] = session
        return session

    def get(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)

    def remove(self, session_id: str) -> Session | None:
        return self._sessions.pop(session_id, None)

    @property
    def count(self) -> int:
        return len(self._sessions)

    @property
    def max_sessions(self) -> int:
        return self._max_sessions
