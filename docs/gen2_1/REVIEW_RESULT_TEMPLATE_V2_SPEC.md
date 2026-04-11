# REVIEW_RESULT_TEMPLATE_V2_SPEC — Gen2.1 Design Spec

This document defines the proposed **v2 review result template** for Gen2.1.

The purpose of v2 is to improve:

- human usability
- output clarity
- ingest safety
- future compatibility with weekly summary and mistake-pattern features

This is a template/interface upgrade only. It must not redesign frozen Gen2 core behavior.

---

## 1. Why This Template Matters Most

Among the current template artifacts, `review_result_template.md` is the most operationally sensitive because it sits at the boundary between:

- the review session
- the user's manual edits
- the ingest pipeline

If this file is confusing or fragile, the workflow becomes easier to break.

So the main design objective is:

**make the template easier for humans while making the ingest boundary more explicit**

---

## 2. Design Goals

The v2 template should:

1. clearly separate editable and non-editable sections
2. keep result capture consistent across sessions
3. reduce accidental damage to the machine-readable block
4. improve readability of the review record
5. support future reporting features without changing current core logic

---

## 3. Non-Goals

The v2 template should not:

- change policy logic
- change scheduler behavior
- change review result semantics
- require schema migration
- require redesign of `services/ingest_service.py`
- introduce new result classes beyond the current baseline

Current result semantics remain:

- `correct`
- `partial`
- `wrong`

---

## 4. Frozen Boundary

Do not redesign or casually modify:

- `domain/policy.py`
- `domain/scheduler.py`
- `services/ingest_service.py`
- `storage/session_repo.py`

Template improvement should happen at the interface/document/output layer.

---

## 5. Main Structural Changes

The v2 template should have four clearly different areas:

1. session header
2. human-editable summary section
3. human-editable structured status section
4. protected machine section

The current key improvement is not “more content”.
The key improvement is **better section boundaries**.

---

## 6. Recommended Template Structure

# Header
- title
- session date
- session id
- generated from review plan note
- short editing warning

# Human-editable summary section
- recall summary
- usage summary
- concept summary
- weak words
- pattern mistakes
- next action

# Human-editable status table
Suggested columns:

- Word
- Result
- Confidence
- Notes
- Follow-up

# Machine section
- one authoritative machine-readable block
- JSON only inside the block
- no prose inside the JSON block

---

## 7. Human-Editable Section Rules

The template should visibly say:

- this section is for human editing
- you may write naturally here
- do not worry about parser syntax here

This reduces the chance that the user edits the wrong part.

Recommended visible label:

```text
HUMAN-EDITABLE SECTION
```

---

## 8. Status Table Rules

The status table should be easy to fill and easy to scan later.

Recommended columns:

- `Word`
- `Result`
- `Confidence`
- `Notes`
- `Suggested Follow-up`

### Required rule
`Result` must stay constrained to:

- `correct`
- `partial`
- `wrong`

### Optional rule
`Confidence` can be a lightweight human field such as:

- high
- medium
- low

This can remain human-facing only unless later explicitly adopted downstream.

---

## 9. Pattern Mistakes Section

The v2 template should make pattern mistakes more reusable.

Suggested per-entry structure:

- Pattern:
- Affected words:
- What went wrong:
- Suggested fix:

This is valuable because it creates better material for future mistake-pattern reporting without changing current storage or policy semantics.

---

## 10. Machine Section Rules

This is the most important safety area.

Recommended visible label:

```text
MACHINE SECTION — DO NOT EDIT STRUCTURE
```

The machine block should remain:

- at the bottom of the file
- single-source-of-truth for per-word machine data
- JSON only
- stable in key naming
- free of extra prose

Recommended edit guidance near the block:

- You may update result values if needed.
- Do not delete keys.
- Do not add commentary inside JSON.
- Do not change quote style.
- Do not convert syntax into rich formatting.

---

## 11. Compatibility Guidance

The v2 template should preserve current ingest compatibility as much as possible.

That means:

1. do not rename core machine keys without necessity
2. do not change result vocabulary
3. keep one item entry per review word
4. keep the existing machine-block concept intact

If a prettier format conflicts with ingest safety, prefer ingest safety.

---

## 12. Suggested Minimal Service-Layer Work

Likely safe touch point:

- `services/review_template_service.py`

Possible secondary updates:

- `services/review_prompt_service.py`
- `USER_GUIDE.md`
- `REBUILD_AND_SMOKE.md`

Parser-layer updates should be minimized unless truly necessary.

---

## 13. Acceptance Criteria

The v2 template should be considered successful when:

1. a user can immediately tell which sections are safe to edit
2. the status table is easier to fill than the current version
3. the machine section is visibly protected
4. current review ingest still works
5. the document creates better future material for summary and mistake reporting

---

## 14. Bottom Line

`review_result_template.md` v2 should be treated as a **boundary-hardening upgrade**.

It should make the current workflow:

- clearer
- safer
- more consistent
- easier to extend later

without changing frozen Gen2 behavior.
