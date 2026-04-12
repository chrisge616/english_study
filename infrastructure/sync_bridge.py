from __future__ import annotations

import shutil
from pathlib import Path

from infrastructure.path_resolver import SyncPaths, is_excluded


class OutputSyncBridge:
    def __init__(self, paths: SyncPaths) -> None:
        self.paths = paths

    def sync_output_to_obsidian(self) -> dict:
        self.paths.notes_output_dir.mkdir(parents=True, exist_ok=True)

        copied_files: list[str] = []
        for source in sorted(self.paths.canonical_output_dir.glob("*.md")):
            relative_path = source.relative_to(self.paths.canonical_root)
            if is_excluded(relative_path):
                continue

            destination = self.paths.notes_output_dir / source.name
            shutil.copy2(source, destination)
            copied_files.append(str(relative_path))

        return {
            "copied_files": copied_files,
            "destination_root": str(self.paths.notes_output_dir),
        }
