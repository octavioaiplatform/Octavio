from typing import Any


ALLOWED_CONTEXT_KEYS = {"npc_id", "location", "world_time", "conversation_state", "player_summary"}


class ContextManager:
    def build(self, character_id: str, updates: dict[str, Any] | None = None) -> dict[str, str]:
        safe_updates = updates or {}
        return {
            "character_id": character_id,
            **{
                key: str(value)[:500]
                for key, value in safe_updates.items()
                if key in ALLOWED_CONTEXT_KEYS and value is not None
            },
        }
