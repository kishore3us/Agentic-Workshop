# Local seed data contract

Run `uv run python load_seed.py` to load the read-only CSVs into repository-root `app.db` as SQLite tables:

| Source | Table | Columns |
| --- | --- | --- |
| `seed/tickets.csv` | `tickets` | `ticket_id`, `customer_id`, `created_at`, `text` |
| `seed/customers.csv` | `customers` | `customer_id`, `name`, `plan`, `open_tickets` |

The table columns and row values match their CSV sources. A second run leaves the same logical tables, columns, and rows without duplicates. `open_tickets` remains numeric so the existing MCP result supports the Enterprise threshold rule.

`mcp/triage_server.py` reads this database from the repository root. Its unchanged `get_ticket` query reads all four ticket columns by `ticket_id`; `get_customer_history` reads all four customer columns by `customer_id` and the matching ticket IDs. Both tools must keep working after the load.
