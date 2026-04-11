from dataclasses import dataclass, field
from typing import Optional


@dataclass
class WordState:
    word_id: int
    status: str
    memory_strength: float = 0.0
    difficulty_score: float = 0.0
    stability_score: float = 0.0
    due_at: Optional[str] = None
    last_seen_at: Optional[str] = None
    last_reviewed_at: Optional[str] = None
    correct_streak: int = 0
    wrong_streak: int = 0


@dataclass
class Evidence:
    word_id: int
    session_id: str
    evidence_type: str
    source: str
    created_at: str
    strength: float = 1.0
    payload: dict = field(default_factory=dict)
