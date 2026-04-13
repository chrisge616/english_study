# Windows WSL Diagnosis

Use this skill when a launcher, browser-open path, WSL reachability path, or Windows-to-WSL integration issue needs diagnosis.

## Rules
- Confirm whether the issue is app logic, launcher logic, or environment reachability before changing code.
- Prefer read-only checks first: WSL distro, repo path, listener state, reachable URL, and current WSL IP.
- Related launcher/UI hardening issues may be grouped into one bounded hardening patch when they solve the same acceptance gap.
- Do not commit diagnostic-only changes unless they directly close the acceptance gap.
