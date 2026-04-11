from pathlib import Path
from .config import ROOT, DATA_DIR, OUTPUT_DIR


LOGS_DIR = ROOT / "logs"
DAILY_LOGS_DIR = LOGS_DIR / "daily"
REVIEW_LOGS_DIR = LOGS_DIR / "review"


def ensure_runtime_dirs() -> None:
    for path in [ROOT, DATA_DIR, OUTPUT_DIR, LOGS_DIR, DAILY_LOGS_DIR, REVIEW_LOGS_DIR]:
        Path(path).mkdir(parents=True, exist_ok=True)
