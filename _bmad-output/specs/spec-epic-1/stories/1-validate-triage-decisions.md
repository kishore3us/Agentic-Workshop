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

### Review Findings

- [x] [Review][Patch] Detect sentence breaks after adjacent lowercase text and closing quotes or brackets [triage_schema.py:55] — medium. `The account is down!please help.` and `The error says "failed." Restart the service.` both validate as one sentence. Sources: blind-hunter, edge-case-hunter, verification-gap, acceptance-auditor.
- [x] [Review][Patch] Do not exempt an abbreviation when it ends a sentence [triage_schema.py:68] — medium. `The user is in the U.S. Needs access.` validates. Sources: blind-hunter, edge-case-hunter, acceptance-auditor.
- [x] [Review][Patch] Accept valid sentences containing initials and common abbreviations [triage_schema.py:26] — medium. `A. Smith cannot log in.`, `Acme Inc. reports a billing failure.`, `The U.S.A. customer cannot log in.`, and `The outage began at 5 p.m. yesterday.` are rejected. Sources: blind-hunter, edge-case-hunter, acceptance-auditor.
- [x] [Review][Patch] Accept a mid-sentence ellipsis [triage_schema.py:50] — low. `We tried... but the page still fails.` is rejected. Source: blind-hunter.
- [x] [Review][Patch] Reject separate statements split by a line break [triage_schema.py:50] — medium. `The account is locked\nReset access` validates as one sentence. Source: blind-hunter.
- [x] [Review][Patch] Recognize non-ASCII sentence terminators [triage_schema.py:50] — low. `問題があります。対応してください。` validates despite containing two sentences. Source: blind-hunter.
- [x] [Review][Patch] Test omission of each required field [tests/test_triage_schema.py:79] — low. Only missing `rationale` is covered; omitting `category`, `priority`, or `route` is untested. Source: verification-gap.
- [x] [Review][Patch] Test two sentences separated by `!` and `?` [tests/test_triage_schema.py:58] — low. All multi-sentence rejection tests use a period. Source: verification-gap.

Rejected:
- [Review][Rejected][low] Quadratic scan on very long punctuation-heavy rationales [triage_schema.py:50] — verified (250, 500, 1000, and 2000 periods took about 0.002, 0.007, 0.026, and 0.103 seconds), but such input is unlikely in normal agent output and an optimization would add complexity. Source: edge-case-hunter.
