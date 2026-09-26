---
title: Decision schema validation
type: 'feature'
created: '2026-09-26'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/_bmad-output/specs/spec-epic-1/SPEC.md'
  - '{project-root}/TRIAGE_POLICY.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Later triage work needs a reliable, machine-checkable contract for every decision so malformed or inconsistent decisions cannot pass through as valid.

**Approach:** Add a reusable Pydantic decision model and validation function for the exact four-field JSON shape. Enforce the category, priority, and category-to-route rules and return clear errors for invalid input; require a rationale string without mechanically counting sentences.

</frozen-after-approval>

## Implementation Notes

- Follow the existing Epic 1 checkpoint API in `origin/stage-2:triage/schema.py`: expose `TriageDecision`, `TriageValidationError`, and `validate_decision(payload: str | bytes | dict)` for structured agent output and explicit JSON validation.
- Use the project’s existing Pydantic dependency. Reject additional properties; enforce the category-to-route pairs in `TRIAGE_POLICY.md`; reject missing fields, invalid enum values, malformed JSON, and non-object inputs with field-specific errors.
- Do not parse sentence count for rationale or normalize nonblank rationale text. Add focused schema tests for successful dict/JSON validation, every invalid path above, each category-route mismatch, and whitespace preservation.
- Keep this story limited to the decision schema and its tests. Do not implement the seed loader or modify the policy, MCP server, or seed files.
- Added `triage/schema.py`, its package initializer, and `tests/test_schema.py`; configured pytest to add the repository root to its import path so the documented `uv run pytest` command can load `triage`.
- Validation errors name the failing field, including the `route` field for category-route mismatches. Nonblank rationale text is preserved exactly.
- Review clarified that the contract validates the rationale's string type without imposing a nonblank rule; JSON text also rejects duplicate keys and wraps recursion errors as validation failures.

## Review Triage Log

- `medium` — patched: a nonblank rationale rule exceeded the contract's string-type requirement; removed it and aligned the test and implementation notes with the spec.
- `medium` — patched: duplicate JSON property names were collapsed by the standard parser; added duplicate-key rejection and coverage.
- `medium` — patched: deeply nested JSON could leak `RecursionError`; it is now converted to `TriageValidationError` and covered by a regression test.
- `low` — patched: the immutability test accepted any exception; it now requires Pydantic's `ValidationError` with the frozen-instance message.
