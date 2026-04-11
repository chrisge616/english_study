import json
import re


BLOCK_RE = re.compile(
    r"<!--\s*STUDY_SESSION_DATA\s*(\{.*?\})\s*-->",
    flags=re.DOTALL,
)


def extract_machine_block(markdown: str) -> dict | None:
    match = BLOCK_RE.search(markdown)
    if not match:
        return None
    return json.loads(match.group(1))
