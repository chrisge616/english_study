from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "study.db"
OUTPUT_DIR = ROOT / "output"
REVIEW_PLAN_PATH = OUTPUT_DIR / "review_plan.md"
DAILY_PROMPT_PATH = OUTPUT_DIR / "daily_prompt.md"
REVIEW_PROMPT_PATH = OUTPUT_DIR / "review_prompt.md"
REVIEW_RESULT_TEMPLATE_PATH = OUTPUT_DIR / "review_result_template.md"


@dataclass(frozen=True)
class ReviewConfig:
    max_items: int = 12
    archived_ratio: float = 0.08
    new_ratio_cap: float = 0.30


REVIEW_CONFIG = ReviewConfig()
