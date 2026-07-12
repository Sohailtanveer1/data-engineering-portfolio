# ADR-0002: Ephemeral Dataproc Clusters as Default Compute Pattern

**Status:** Accepted
**Date:** See [`00-project-overview/04-timeline-and-phases.md`](../00-project-overview/04-timeline-and-phases.md) Foundation phase
**Deciders:** Migration Program Lead, Platform Engineering

## Context

On-prem, all Spark jobs share one fixed-capacity YARN cluster, causing the
two dominant pain points identified in
[`03-current-environment/09-pain-points-and-bottlenecks.md`](../03-current-environment/09-pain-points-and-bottlenecks.md):
capacity that's insufficient at peak and wasted off-peak, and queue
contention causing job delays. The target compute pattern needs to
resolve both.

## Decision

Ephemeral, per-job (or per-job-family) Dataproc clusters are the default
compute pattern, created and torn down by Composer per job run — per
[`04-target-architecture/03-compute-architecture.md`](../04-target-architecture/03-compute-architecture.md).
Persistent clusters are the explicitly-justified exception (streaming,
very-high-frequency jobs, interactive workloads).

## Alternatives Considered

| Alternative | Why Not Chosen |
|---|---|
| Persistent shared cluster (status quo pattern, lifted to GCP) | Directly reproduces the fixed-capacity and contention problems the migration is meant to solve |
| Dataproc Serverless as the universal default | Better fit reserved specifically for irregular/unpredictable workloads (per [`04-target-architecture/03-compute-architecture.md`](../04-target-architecture/03-compute-architecture.md)); scheduled, predictable batch jobs benefit from the more configurable, tunable ephemeral-cluster pattern for performance tuning per [`17-performance/`](../17-performance/README.md) |

## Consequences

**Positive:**
- No idle capacity cost — directly supports the cost-efficiency half of
  the business case.
- No queue contention between job families.
- Right-sized per job family, informed by real resource footprint data.

**Negative / Tradeoffs Accepted:**
- Cluster startup time adds overhead to every job run — mitigated via
  custom images and minimal init actions per
  [`12-cluster-design/07-initialization-actions-and-custom-images.md`](../12-cluster-design/07-initialization-actions-and-custom-images.md),
  and explicitly budgeted into SLA calculations.
- More cluster configurations to manage (one per job family) — mitigated
  by the standardized, Terraform-templated approach in
  [`12-cluster-design/`](../12-cluster-design/README.md).

## Related Documents

[`04-target-architecture/03-compute-architecture.md`](../04-target-architecture/03-compute-architecture.md),
[`12-cluster-design/01-cluster-topology-decision.md`](../12-cluster-design/01-cluster-topology-decision.md),
[`04-target-architecture/10-pain-point-traceability.md`](../04-target-architecture/10-pain-point-traceability.md)
