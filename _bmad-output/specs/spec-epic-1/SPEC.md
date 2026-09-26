---
id: SPEC-epic-1
companions: [../../../TRIAGE_POLICY.md, ../../../mcp/triage_server.py]
sources: [../../../INTENT.md]
---

> **Canonical contract.** This SPEC and the files in `companions:` are the complete, preservation-validated contract for what to build, test, and validate. Source documents listed in frontmatter are for traceability — consult them only if you need narrative rationale or prose color this contract intentionally omits.

# Epic 1: triage data and schema

## Why

This workshop needs a reliable foundation for ticket triage: a machine-checkable decision contract and repeatably loaded local ticket and customer records for the existing MCP server. Epic 1 makes the data and output shape stable for later agent work.

## Capabilities

- **CAP-1**
  - **intent:** A caller can submit a triage decision and get a clear validation error when it does not match the decision contract.
  - **success:** Accepted JSON objects contain exactly `category`, `priority`, `route`, and `rationale`. The category is `billing`, `bug`, `access`, `performance`, or `how-to`; the priority is `P1` through `P4`; and the route matches the category mapping in `TRIAGE_POLICY.md`. The rationale is a required string intended to contain one sentence; extra properties and invalid or missing fields are rejected with a clear error. Sentence count is a content requirement and is not parsed mechanically.

- **CAP-2**
  - **intent:** A developer can populate the local database from the provided ticket and customer CSV files for use by the existing triage server.
  - **success:** `uv run python load_seed.py` loads `seed/tickets.csv` into the local SQLite file `app.db`, table `tickets`, with the columns `ticket_id`, `customer_id`, `created_at`, and `text`, and `seed/customers.csv` into table `customers` with the columns `customer_id`, `name`, `plan`, and `open_tickets`. Running the command twice produces the same database.

## Constraints

- Use Python 3.12 or newer, managed with uv.
- Treat every file in `seed/` as read-only.
- Make no network calls and require no API keys.
- Preserve the `app.db` table and column names queried by `mcp/triage_server.py`.
- Use `TRIAGE_POLICY.md` as the read-only authority for category-to-route pairings.

## Non-goals

- Building the agent or changing the MCP tools.
- Building evaluations or a user interface.

## Success signal

Running `uv run python load_seed.py` creates `app.db` with the required tables and columns, and a second run leaves the same database; valid decisions match the decision contract while invalid ones receive a clear error.

## Assumptions

- Category-to-route pairings follow the mapping in `TRIAGE_POLICY.md`.
- Decision objects reject properties beyond the four named fields, following the intent that anything else is rejected.
- The one-sentence rationale is a content requirement; the schema validator checks that the rationale field is a string but does not parse sentence count.
