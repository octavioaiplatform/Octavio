from pathlib import Path

import pytest

from app.characters.manager import CharacterManager
from app.context.manager import ContextManager
from app.sessions.manager import SessionManager


def test_character_manager_loads_marcos():
    character = CharacterManager().get("marcos")
    assert character.language == "es"
    assert "Puerto Claro" in character.description


def test_character_manager_rejects_duplicate_ids(tmp_path: Path):
    template = "id: same\nname: A\ndescription: D\npersonality: P\ninstructions: I\n"
    (tmp_path / "a.yaml").write_text(template, encoding="utf-8")
    (tmp_path / "b.yaml").write_text(template.replace("name: A", "name: B"), encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate character id"):
        CharacterManager(tmp_path)


def test_context_manager_filters_unapproved_fields():
    context = ContextManager().build("marcos", {"location": "plaza", "secret": "discard", "player_summary": "visitor"})
    assert context == {"character_id": "marcos", "location": "plaza", "player_summary": "visitor"}


def test_session_manager_enforces_capacity():
    manager = SessionManager(max_sessions=1)
    manager.create("marcos")
    with pytest.raises(RuntimeError, match="Maximum concurrent sessions"):
        manager.create("marcos")
