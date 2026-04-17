from __future__ import annotations

from dataclasses import dataclass

from app.config import (
    ROOT,
    get_db_path,
    get_db_path_source,
    get_notes_workspace,
    get_notes_workspace_source,
)


@dataclass(frozen=True)
class PathContext:
    canonical_engine_repo: str
    notes_workspace: str
    notes_workspace_source: str
    database_path: str
    database_path_source: str

    @classmethod
    def from_defaults(cls) -> "PathContext":
        return cls(
            canonical_engine_repo=str(ROOT),
            notes_workspace=get_notes_workspace(),
            notes_workspace_source=str(get_notes_workspace_source()),
            database_path=str(get_db_path()),
            database_path_source=str(get_db_path_source()),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "canonical_engine_repo": self.canonical_engine_repo,
            "notes_workspace": self.notes_workspace,
            "notes_workspace_source": self.notes_workspace_source,
            "database_path": self.database_path,
            "database_path_source": self.database_path_source,
        }
