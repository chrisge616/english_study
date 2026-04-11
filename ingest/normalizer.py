STATUS_MAP = {
    "❌": "NEW",
    "△": "WEAK",
    "○": "STABLE",
    "✅": "STRONG",
    "🧊": "ARCHIVED",
    "NEW": "NEW",
    "WEAK": "WEAK",
    "STABLE": "STABLE",
    "STRONG": "STRONG",
    "ARCHIVED": "ARCHIVED",
}


def normalize_status(value: str) -> str:
    return STATUS_MAP.get(value.strip(), value.strip().upper())
