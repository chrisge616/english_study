from enum import Enum


class Status(str, Enum):
    NEW = "NEW"
    WEAK = "WEAK"
    STABLE = "STABLE"
    STRONG = "STRONG"
    ARCHIVED = "ARCHIVED"


class EvidenceType(str, Enum):
    INTRODUCED = "introduced"
    MARKED_DIFFICULT = "marked_difficult"
    MARKED_FAMILIAR = "marked_familiar"
    APPEARED_IN_MISTAKE = "appeared_in_mistake"
    REVIEW_CORRECT = "review_correct"
    REVIEW_PARTIAL = "review_partial"
    REVIEW_WRONG = "review_wrong"
    MANUAL_OVERRIDE = "manual_override"
