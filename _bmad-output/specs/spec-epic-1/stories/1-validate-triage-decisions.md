---
title: 'Validate triage decisions'
type: 'feature'
created: '2026-09-26'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The later agent and eval epics need a reusable contract that rejects malformed triage decisions before they are used.

**Approach:** Provide a Python decision schema for exactly `category`, `priority`, `route`, and a one-sentence `rationale`, enforcing the allowed values and category-to-route pairing in `decision-schema.md` with clear validation errors. Classification and priority judgment for a ticket remain outside this story.

</frozen-after-approval>

## Implementation Notes

- Added `triage_schema.py` with a strict Pydantic `TriageDecision` model. It rejects unknown fields and values, mismatched category/route pairs, blank rationales, and detectable multiple sentences. It leaves ticket classification to later epics.
- Added `tests/test_triage_schema.py` for the allowed pairs and priorities, malformed objects, wrong values, and rationale edge cases.
- `uv run pytest` could not initially import a root module from `tests/`; set pytest's `pythonpath` to the repository root in `pyproject.toml`.
- The review exposed four rationale edge cases. Expanded the sentence check to reject adjacent sentence text and punctuation-only values while accepting common abbreviations. The focused suite passed with 24 tests.

## Review Triage Log

- medium — Confirmed `First.second` passed because the original boundary check only recognized an uppercase word without a space. Patched the boundary check and added a regression test.
- medium — Confirmed `Access failed, etc. Reset the account.` passed because `etc.` was always ignored. Removed that exception and added a regression test.
- medium — Confirmed valid `U.S.` and `Jan.` rationales failed because the abbreviation list and initials check were incomplete. Patched both and added regression cases.
- medium — Confirmed `...` passed despite containing no sentence content. Require at least one letter and added a regression test.
