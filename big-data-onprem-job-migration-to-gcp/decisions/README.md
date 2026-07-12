# decisions — Architecture Decision Log

## Purpose

Full Architecture Decision Records (ADRs) for decisions with program-wide,
long-term impact — promoted here from the phase-level decision logs (e.g.,
[`04-target-architecture/09-architecture-decision-log.md`](../04-target-architecture/09-architecture-decision-log.md))
when a decision affects more than one phase, would be expensive to
reverse, or a future engineer would reasonably ask "why did we do it this
way?" without obvious context.

## Owner

Migration Program Lead.

## ADR format

Every ADR uses [`template.md`](template.md) — Context, Decision,
Alternatives Considered, Consequences, Status.

## ADR Index

| ADR | Title | Status |
|---|---|---|
| [ADR-0001](ADR-0001-full-environment-isolation.md) | Full GCP project isolation per environment | Accepted |
| [ADR-0002](ADR-0002-ephemeral-dataproc-clusters.md) | Ephemeral Dataproc clusters as default compute pattern | Accepted |
| [ADR-0003](ADR-0003-per-table-warehouse-decision-framework.md) | Per-table BigQuery vs. Dataproc-Hive decision framework | Accepted |
| [ADR-0004](ADR-0004-secret-manager-mandatory.md) | Secret Manager mandatory, no plaintext credentials | Accepted |

## When to write a new ADR

Per the promotion criteria in
[`04-target-architecture/09-architecture-decision-log.md`](../04-target-architecture/09-architecture-decision-log.md)
— not every decision needs a full ADR; most are adequately captured in
their owning phase document. Write one here when the decision crosses
phase boundaries or would be genuinely confusing to a future reader
without the "why."
