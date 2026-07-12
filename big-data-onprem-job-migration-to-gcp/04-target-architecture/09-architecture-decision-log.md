# Architecture Decision Log (Phase-Level Summary)

**Purpose:** A running log of the key decisions made while building this
target architecture, each with its alternatives considered and rationale.
This is the phase-level summary; formal, fully detailed Architecture
Decision Records (ADRs) for decisions with program-wide, long-term impact
are filed in [`decisions/`](../decisions/README.md) using the standard ADR
template there.
**Owner:** Migration Program Lead.
**When to promote a decision here to a full ADR in `decisions/`:** if it
affects more than one phase folder, would be expensive to reverse, or a
future engineer would reasonably ask "why did we do it this way?" without
obvious context.

---

## Decision log

| # | Decision | Alternatives Considered | Rationale | Full ADR? |
|---|---|---|---|---|
| D1 | Full GCP project isolation per environment (dev/qa/stage/prod), not shared-project namespacing | Shared project with logical namespacing | Cleaner IAM boundaries, quota/billing separation, matches constraint C4 | Yes — [`decisions/`](../decisions/README.md) ADR-0001 |
| D2 | Ephemeral Dataproc clusters as the default compute pattern | Persistent shared cluster (status quo pattern); Dataproc Serverless as default | Directly resolves capacity and contention pain points from `03-current-environment/`; Serverless reserved for irregular workloads specifically | Yes — ADR-0002 |
| D3 | Per-table BigQuery vs. Dataproc-Hive decision framework, not a blanket rule | BigQuery for everything; Dataproc-Hive for everything | Neither blanket rule captures the real cost/performance/governance tradeoffs across a heterogeneous table estate | Yes — ADR-0003 |
| D4 | Parquet as the standard target file format, converting legacy formats during migration | Preserve original formats as-is | Resolves pain point #5 (legacy format cost); avoids carrying forward inefficiency | No — captured sufficiently in [`04-storage-architecture.md`](04-storage-architecture.md) |
| D5 | DAGs organized by business domain, not technical job type | Organize by technical layer (extract/transform/load) | Matches existing team ownership model, minimizes cognitive shift for job owners | No |
| D6 | All secrets via Secret Manager; no plaintext credentials anywhere | Continue current per-job credential storage patterns | Closes explicit security findings from Discovery; required by security architecture principles | Yes — ADR-0004 |
| D7 | Connectivity method (VPN vs. Interconnect) decided by measured transfer volume, deferred to `11-network/` for final sizing | Default to VPN for simplicity; default to Interconnect for headroom | Avoids both under-provisioning (VPN insufficient for real volume) and over-spending (Interconnect where unneeded) without first measuring actual requirement | No — tracked as an open item for `11-network/` |

_(This log grows as the architecture is refined during
[`12-cluster-design/`](../12-cluster-design/README.md) and
[`13-infrastructure/`](../13-infrastructure/README.md) implementation
work surfaces new decisions — it is not closed once this folder is gated.)_

## Open decisions carried forward

| # | Open Decision | Owner | Target Resolution Phase |
|---|---|---|---|
| O1 | Final connectivity method (VPN vs. Interconnect) | Network Engineering | [`11-network/`](../11-network/README.md) |
| O2 | Streaming architecture for Kafka-sourced workloads (Pub/Sub redesign vs. self-managed Kafka) | Platform Engineering | [`04-target-architecture/`](README.md) refinement / [`06-data-migration/`](../06-data-migration/README.md) |
| O3 | Final per-table BigQuery vs. Dataproc-Hive assignment for every table (framework defined, application pending) | Data Engineering | [`08-hive-migration/`](../08-hive-migration/README.md) |

## How to use this log

Before proposing a new architectural direction in any later phase, check
this log first — if a related decision was already made and rejected here,
either respect it or explicitly propose reopening it (with a new
justification) rather than silently re-deciding it differently in a
downstream document, which produces internal inconsistency across the
repository.
