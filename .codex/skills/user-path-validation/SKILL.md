# User Path Validation

Use this skill when a change affects user-facing paths, launchers, workspace detection, or Windows/WSL path handoff.

## Rules
- Validate the real path in the current environment before commit.
- Prefer direct runtime/path checks over assumptions.
- If the path differs between Windows and WSL, report both forms.
- If validation is inconclusive after two failed patch attempts on the same path, stop editing and switch to read-only diagnosis.
