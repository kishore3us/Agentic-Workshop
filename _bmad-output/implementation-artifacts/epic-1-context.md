# Epic 1 Context: Triage Data and Schema

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Establish a strict triage decision contract and repeatable local ticket and customer data so the later agent and evaluation work can rely on predictable inputs and outputs. No separate PRD, architecture, UX/design, or product brief was available; this context draws from the Epic 1 spec and its companion contracts.

## Stories

- Story 1.1: Validate triage decisions
- Story 1.2: Load local seed data

## Requirements & Constraints

- Accept only a JSON decision object with the exact required fields, permitted category and priority values, a route matching the category, and a one-sentence rationale. Reject invalid decisions with clear validation errors. The agent epic determines whether a valid decision is correct for a ticket.
- Initialize the repository-root `app.db` from both read-only seed CSVs with `uv run python load_seed.py`. Preserve their specified columns and row values. Repeated runs must leave the same logical tables and rows without duplicates; byte-identical SQLite files are not required.
- Keep customer `open_tickets` numeric and preserve compatibility with the existing ticket and customer-history MCP queries.
- Make no network calls and use no API keys in this epic. Do not build the agent, change MCP tools, add evaluations, or add a user interface.

## Technical Decisions

- Use Python 3.12 or newer, managed with uv, and SQLite at the repository-root `app.db`.
- Keep the existing `mcp/triage_server.py` unchanged. The database must expose `tickets` and `customers` with the columns specified by the data contract so both MCP lookups work after loading.
- Treat `seed/` and `TRIAGE_POLICY.md` as read-only. Do not commit `app.db`.

## Cross-Story Dependencies

The schema validator and seed loader are separate foundations for the later agent and evaluation epics. The story order is schema first, then loader; neither implementation requires the other to run.
