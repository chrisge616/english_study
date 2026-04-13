from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from application.path_context import PathContext


EXCLUDED_NAMES = {
    ".git",
    ".venv",
    "__pycache__",
    "english_study.egg-info",
    ".pytest_cache",
}

EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


@dataclass(frozen=True)
class SyncPaths:
    canonical_root: Path
    notes_workspace_windows: str
    notes_workspace_wsl: Path
    canonical_output_dir: Path
    notes_output_dir: Path
    canonical_daily_logs_dir: Path
    notes_daily_logs_dir: Path


def build_sync_paths(path_context: PathContext) -> SyncPaths:
    canonical_root = Path(path_context.canonical_engine_repo)
    notes_workspace_wsl = windows_path_to_wsl(path_context.notes_workspace)
    return SyncPaths(
        canonical_root=canonical_root,
        notes_workspace_windows=path_context.notes_workspace,
        notes_workspace_wsl=notes_workspace_wsl,
        canonical_output_dir=canonical_root / "output",
        notes_output_dir=notes_workspace_wsl / "output",
        canonical_daily_logs_dir=canonical_root / "logs" / "daily",
        notes_daily_logs_dir=notes_workspace_wsl / "logs" / "daily",
    )


def windows_path_to_wsl(path_text: str) -> Path:
    win_path = PureWindowsPath(path_text)
    drive = win_path.drive.rstrip(":").lower()
    root = f"{win_path.drive}\\"
    parts = [part for part in win_path.parts if part not in {win_path.drive, root}]
    return Path("/mnt") / drive / Path(*parts)


def is_excluded(relative_path: Path) -> bool:
    if any(part in EXCLUDED_NAMES for part in relative_path.parts):
        return True
    return relative_path.suffix.lower() in EXCLUDED_SUFFIXES
