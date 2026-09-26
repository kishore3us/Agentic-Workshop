# Triage decision contract

Each decision is a JSON object with exactly these four fields:

| Field | Allowed value |
| --- | --- |
| `category` | `billing`, `bug`, `access`, `performance`, or `how-to` |
| `priority` | `P1`, `P2`, `P3`, or `P4` |
| `route` | The team route paired with `category` below |
| `rationale` | One sentence |

| Category | Route |
| --- | --- |
| `billing` | `billing-team` |
| `bug` | `bug-team` |
| `access` | `access-team` |
| `performance` | `performance-team` |
| `how-to` | `how-to-team` |

Reject non-object JSON, missing or extra fields, values outside these sets, a route that does not match its category, or a rationale that is not one sentence. Give a clear validation error. This contract validates decision shape and allowed values; deciding the correct category or priority for a ticket belongs to the agent epic.
