# Change Data Capture (CDC) Strategy

**Purpose:** Define when full CDC (capturing inserts, updates, *and*
deletes, in order) is required versus when the simpler watermark-based
incremental pattern in
[`02-incremental-load-strategy.md`](02-incremental-load-strategy.md) is
sufficient — CDC is more complex and costly to build and operate, and
should be reserved for cases that genuinely need it.
**Owner:** Data Engineering.

---

## When CDC is required

| Signal | CDC Required? |
|---|---|
| Source system performs hard deletes that downstream consumers must reflect | Yes |
| Source system performs updates-in-place (not append-only) that must be reflected with full history/audit trail | Yes — CDC preserves the change sequence; a periodic full-table watermark re-extract does not |
| Business requirement for near-real-time propagation of source changes (sub-minute/sub-5-minute latency) | Yes, typically |
| Source is append-only (e.g., an event log, an immutable order-line table) | No — watermark-based incremental load is sufficient and simpler |
| Periodic (hourly/daily) batch freshness is acceptable per the SLA in [`01-discovery/inventories/01-sla-inventory.md`](../01-discovery/inventories/01-sla-inventory.md) | No |

## Candidate sources for CDC in this environment

Based on the application inventory
([`01-discovery/inventories/07-application-inventory.md`](../01-discovery/inventories/07-application-inventory.md)),
evaluate CDC specifically for:

| Source | Why CDC May Be Needed | Recommended Approach |
|---|---|---|
| OMS (Order Management System) | Orders are updated through their lifecycle (placed → fulfilled → returned); downstream fraud/finance need to see status transitions, not just final state | Datastream (GCP-native CDC for supported database engines) if the OMS database engine is supported; otherwise a custom log-based or trigger-based CDC approach coordinated with the OMS team |
| WMS (Warehouse Management System) | Inventory levels change continuously and deletes/corrections happen | Evaluate whether the existing Kafka-based integration (per [`01-discovery/inventories/07-application-inventory.md`](../01-discovery/inventories/07-application-inventory.md)) already provides adequate change-event granularity — may not need separate CDC if Kafka already serves this role |
| Payment Gateway reconciliation DB | Financial correctness requires no missed updates/corrections | High governance requirement — CDC strongly recommended if technically feasible; coordinate closely with Payments team given system sensitivity |

## Recommended tooling

| Tool | When to Use |
|---|---|
| **Datastream** (GCP-native) | Preferred default for CDC from supported source databases (MySQL, PostgreSQL, Oracle, SQL Server) directly into BigQuery or GCS — minimizes custom code |
| **Custom Spark Structured Streaming CDC consumer** | If the source already emits a change stream via Kafka (leveraging existing integration patterns from [`01-discovery/inventories/12-external-dependencies.md`](../01-discovery/inventories/12-external-dependencies.md)) |
| **Trigger-based or log-based custom CDC** | Only if neither of the above fits (e.g., an unsupported database engine) — highest implementation and maintenance cost, use only when justified |

## Design requirements for any CDC pipeline built

1. **Ordering guarantees** — changes must be applied to the target in the
   same order they occurred at the source, per key. Confirm the chosen
   tool's ordering guarantees explicitly.
2. **Exactly-once or idempotent-upsert semantics** at the target — a CDC
   pipeline that can duplicate or lose changes on retry is worse than no
   CDC at all for correctness-sensitive domains.
3. **Schema evolution handling** — source schema changes (added/dropped/
   renamed columns) must not silently break the CDC pipeline; define an
   explicit schema-change alerting and handling process.
4. **Monitoring and lag alerting** — per
   [`18-monitoring/`](../18-monitoring/README.md), CDC lag must be visible
   and alertable, since a silently lagging CDC pipeline produces a subtly
   stale target that's easy to miss without explicit monitoring.

## Common Mistakes

- Defaulting to CDC everywhere "to be safe" — this adds substantial
  operational complexity and cost for sources that don't actually need it
  (append-only, batch-SLA-acceptable sources).
- Building custom CDC when a managed option (Datastream) would have
  covered the requirement with far less ongoing maintenance burden.

## Production Notes

For any CDC pipeline touching the payment gateway reconciliation or OMS
data, coordinate design and testing explicitly with the owning team and
Security — these are among the most sensitive data flows in the platform,
and CDC's continuous, always-on nature (versus a scheduled batch job) means
issues can propagate faster if not carefully monitored.
