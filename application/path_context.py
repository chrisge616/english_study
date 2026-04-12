from __future__ import annotations

from dataclasses import dataclass

from app.config import DB_PATH, ROOT


DEFAULT_NOTES_WORKSPACE = r"C:\Users\Chris\Documents\Obsidian Vault\english_study"


@dataclass(frozen=True)
class PathContext:
    canonical_engine_repo: str
    notes_workspace: str
    database_path: str

    @classmethod
    def from_defaults(cls) -> "PathContext":
        return cls(
            canonical_engine_repo=str(ROOT),
            notes_workspace=DEFAULT_NOTES_WORKSPACE,
            database_path=str(DB_PATH),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "canonical_engine_repo": self.canonical_engine_repo,
            "notes_workspace": self.notes_workspace,
            "database_path": self.database_path,
        }
