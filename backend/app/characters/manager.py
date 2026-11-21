from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field


class Character(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    description: str
    personality: str
    language: str = "es"
    voice: str = ""
    instructions: str
    initial_context: str = ""


class CharacterManager:
    def __init__(self, characters_dir: Path | None = None) -> None:
        self._characters_dir = characters_dir or Path(__file__).with_name("data")
        self._characters: dict[str, Character] = {}
        self.reload()

    def reload(self) -> None:
        self._characters.clear()
        for path in sorted(self._characters_dir.glob("*.yaml")):
            character = Character.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
            if character.id in self._characters:
                raise ValueError(f"Duplicate character id: {character.id}")
            self._characters[character.id] = character

    def get(self, character_id: str) -> Character:
        try:
            return self._characters[character_id]
        except KeyError as exc:
            raise KeyError(f"Unknown character: {character_id}") from exc

    def list(self) -> list[Character]:
        return list(self._characters.values())
