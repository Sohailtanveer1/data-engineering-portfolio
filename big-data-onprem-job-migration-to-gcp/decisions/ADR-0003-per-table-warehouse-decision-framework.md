# ADR-0003: Per-Table BigQuery vs. Dataproc-Hive Decision Framework

**Status:** Accepted
**Date:** See [`00-project-overview/04-timeline-and-phases.md`](../00-project-overview/04-timeline-and-phases.md) Foundation phase
**Deciders:** Migration Program Lead, Data Engineering, Platform Engineering

## Context

Every migrated Hive table needs a GCP target: BigQuery or a
Dataproc-managed Hive Metastore pattern. A blanket rule in either
direction (all-BigQuery or all-Dataproc-Hive) was considered against an
explicit per-table decision framework.

## Decision

Adopt an explicit, criteria-based decision framework
([`04-target-architecture/05-data-warehouse-architecture.md`](../04-target-architecture/05-data-warehouse-architecture.md))
applied per table, based on primary consumer, query pattern, governance
need, and cost profile — not a platform-wide default.

## Alternatives Considered

| Alternative | Why Not Chosen |
|---|---|
| BigQuery for every table | Unnecessary cost and complexity for pipeline-internal staging tables never queried directly by humans or BI tools |
| Dataproc-Hive for every table | Forfeits BigQuery's governance (column/row-level security), performance, and serverless scaling benefits for exactly the BI/analyst-facing tables that benefit most |

## Consequences

**Positive:**
- Cost and performance optimized per table's actual usage pattern.
- Governance-sensitive tables (fraud, finance) get BigQuery's stronger
  native access control.

**Negative / Tradeoffs Accepted:**
- More decision-making overhead per table than a blanket rule — mitigated
  by the explicit, repeatable framework and worked examples in
  [`04-target-architecture/05-data-warehouse-architecture.md`](../04-target-architecture/05-data-warehouse-architecture.md),
  which make the decision fast and consistent rather than a fresh debate
  per table.
- Two target platforms to operate and monitor instead of one — accepted
  given the material benefit of matching each table to its best-fit
  platform.

## Related Documents

[`04-target-architecture/05-data-warehouse-architecture.md`](../04-target-architecture/05-data-warehouse-architecture.md),
[`08-hive-migration/01-metastore-migration-strategy.md`](../08-hive-migration/01-metastore-migration-strategy.md),
[`01-discovery/inventories/09-hive-inventory.md`](../01-discovery/inventories/09-hive-inventory.md)
