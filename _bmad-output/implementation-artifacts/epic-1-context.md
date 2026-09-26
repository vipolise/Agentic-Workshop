# Epic 1 Context: triage data and schema

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Establish a reliable foundation for ticket triage by defining a machine-checkable decision contract and repeatably loading local ticket and customer records for the existing MCP server. This stabilizes the data and output shape needed by later agent work. The planning-artifacts directory is absent, so this context is based on the Epic 1 spec and story list only.

## Stories

- Story 1.1: Decision schema validation
- Story 1.2: Idempotent seed loader

## Requirements & Constraints

- Decision validation must accept only the defined triage decision shape and values, reject missing, invalid, or additional fields with a clear error, and use the policy's category-to-route pairings. The rationale must be a string intended to contain one sentence; sentence count is not mechanically checked.
- The seed-loading command must load the supplied ticket and customer CSV data into the local SQLite database with the specified tables and columns. Repeated runs must produce the same database.
- Treat seed files as read-only. Do not make network calls or require API keys.
- The success signal is a valid local database after loading, unchanged by a repeated run, alongside clear validation behavior for valid and invalid decisions.
- Use Python 3.12 or newer, managed with uv. The agent, MCP tools, evaluations, and UI are outside this epic's scope.

## Technical Decisions

- `TRIAGE_POLICY.md` is the read-only authority for category-to-route pairings.
- Preserve the `app.db` table and column names queried by `mcp/triage_server.py`.
- The database is a local SQLite file, and the seed loader is invoked as `uv run python load_seed.py`.
