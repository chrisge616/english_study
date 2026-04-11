# Review Result Template

Session Date: [YYYY-MM-DD]  
Session ID: [review_session_id]  
Generated From: `output/review_plan.md`

This file is used to record the outcome of a review session.

Please fill the human-editable sections normally.  
Keep the machine section at the bottom structurally valid.

---

## HUMAN-EDITABLE SECTION

### 1. Recall Summary
- What was recalled well?
- Which words were remembered only vaguely?
- Which words were missed?

### 2. Usage Summary
- Which words were used correctly in examples?
- Which words showed weak usage control?
- Which words were recognized but not actively usable?

### 3. Concept / Nuance Summary
- Which words were conceptually clear?
- Which words were confused with nearby meanings?
- Which nuance gaps appeared during review?

### 4. Weak Words
- [word]
- [word]
- [word]

### 5. Pattern Mistakes
#### Pattern 1
- Pattern:
- Affected words:
- What went wrong:
- Suggested fix:

#### Pattern 2
- Pattern:
- Affected words:
- What went wrong:
- Suggested fix:

### 6. Next Action
- What should be reinforced next?
- Which words need early review?
- Which words may be stable enough to leave alone for now?

---

## STATUS UPDATE TABLE

| Word | Result | Confidence | Notes | Suggested Follow-up |
|------|--------|------------|-------|---------------------|
| [word_1] | correct / partial / wrong | high / medium / low | [short note] | [short action] |
| [word_2] | correct / partial / wrong | high / medium / low | [short note] | [short action] |
| [word_3] | correct / partial / wrong | high / medium / low | [short note] | [short action] |

Rules:
- `Result` should stay one of: `correct`, `partial`, `wrong`
- Keep notes short and concrete
- Use follow-up only for actionable next steps

---

## MACHINE SECTION — DO NOT EDIT STRUCTURE

You may update result values if needed.  
Do not delete keys.  
Do not add prose inside the JSON.  
Do not change quote style.  
Do not convert this block into rich formatting.

<!-- STUDY_SESSION_DATA
{
  "session_id": "[review_session_id]",
  "session_type": "review",
  "items": [
    {
      "word": "[word_1]",
      "result": "correct",
      "source": "review"
    },
    {
      "word": "[word_2]",
      "result": "partial",
      "source": "review"
    },
    {
      "word": "[word_3]",
      "result": "wrong",
      "source": "review"
    }
  ]
}
-->

---

## FINAL CHECK BEFORE INGEST

Confirm the following:

- the human-editable section is complete enough to keep as a review record
- the status table uses valid `Result` values
- the machine block is still valid JSON
- the session id is correct
- the file is saved under `logs/review/`

Example ingest command:

```powershell
study ingest review ".\logs\review\YYYY-MM-DD_review.md"
```
