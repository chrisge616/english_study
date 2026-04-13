from __future__ import annotations

import filecmp
import shutil

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

    def sync_daily_logs_from_obsidian(self) -> dict:
        source_dir = self.paths.notes_daily_logs_dir
        destination_dir = self.paths.canonical_daily_logs_dir
        destination_dir.mkdir(parents=True, exist_ok=True)

        if not source_dir.exists():
            return {
                "copied_files": [],
                "skipped_files": [],
                "conflicts": [],
                "source_root": str(source_dir),
                "destination_root": str(destination_dir),
            }

        copied_files: list[str] = []
        skipped_files: list[str] = []
        conflicts: list[str] = []

        for source in sorted(source_dir.glob("*.md")):
            relative_path = destination_dir.relative_to(self.paths.canonical_root) / source.name
            if is_excluded(relative_path):
                continue

            destination = destination_dir / source.name
            if not destination.exists():
                shutil.copy2(source, destination)
                copied_files.append(str(relative_path))
                continue

            if filecmp.cmp(source, destination, shallow=False):
                skipped_files.append(str(relative_path))
                continue

            conflicts.append(str(relative_path))

        return {
            "copied_files": copied_files,
            "skipped_files": skipped_files,
            "conflicts": conflicts,
            "source_root": str(source_dir),
            "destination_root": str(destination_dir),
        }
