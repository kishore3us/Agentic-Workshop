---
id: SPEC-epic-1
companions: [decision-schema.md, data-contract.md, ../../../mcp/triage_server.py]
sources: [../../../INTENT.md]
---

> **Canonical contract.** This SPEC and its companions define what to build and verify. `INTENT.md` is listed for traceability; its requirements are absorbed here.

# Epic 1: triage data and schema

## Why

The support-ticket triage workshop needs repeatable local ticket data and a strict decision contract before the later agent and eval epics can use them. The existing MCP server already expects a particular SQLite database shape.

## Capabilities

- **CAP-1**
  - **intent:** A triage decision can be validated as one predictable JSON object for later agent and eval runs.
  - **success:** A decision with the exact fields and allowed values in `decision-schema.md` is accepted; any other shape or value is rejected with a clear error.

- **CAP-2**
  - **intent:** A workshop participant can initialize the local ticket and customer database with one repeatable command.
  - **success:** `uv run python load_seed.py` loads both seed CSVs into `app.db` with the tables, columns, and rows in `data-contract.md`; a second run leaves the same logical database, and the existing MCP queries can read it.

## Constraints

- Use Python 3.12 or newer with uv.
- Do not change files under `seed/`, `TRIAGE_POLICY.md`, or `mcp/triage_server.py`.
- Epic 1 makes no network calls and uses no API keys.
- The SQLite database lives at repository-root `app.db` and remains compatible with the existing MCP server. Do not commit `app.db`.

## Non-goals

- The triage agent, new or changed MCP tools, evals, and any user interface.

## Success signal

A valid triage decision passes validation while invalid decisions fail clearly. Running `uv run python load_seed.py` twice yields the same ticket and customer tables and rows, which `mcp/triage_server.py` can query.

## Assumptions

- “Running it twice gives the same database” means identical logical tables, columns, and rows, not byte-identical SQLite files.
