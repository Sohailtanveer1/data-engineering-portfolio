# 19 — Cost Optimization

## Purpose

Deliver on the cost-efficiency half of the business case in
[`00-project-overview/01-executive-summary.md`](../00-project-overview/01-executive-summary.md)
— trading the current fixed, hardware-bound cost structure for a variable,
usage-optimized one, with the discipline to keep it that way as the
platform grows rather than letting cloud costs drift upward unchecked
(a common failure mode in cloud migrations).

## Owner

**Platform Engineering / Cloud-DevOps**, with Finance as a reviewing
stakeholder per constraint C6.

## Inputs

- Cluster sizing from
  [`12-cluster-design/`](../12-cluster-design/README.md).
- Storage architecture from
  [`04-target-architecture/04-storage-architecture.md`](../04-target-architecture/04-storage-architecture.md).
- Actual billing data once workloads are running.

## Outputs

- A cost baseline and ongoing attribution model.
- Implemented autoscaling, spot/preemptible, and storage tiering
  optimizations.
- A recurring rightsizing review process.
- Budget monitoring with tiered alerts.

## Prerequisites

[`12-cluster-design/`](../12-cluster-design/README.md) and
[`18-monitoring/`](../18-monitoring/README.md) providing the sizing and
observability this folder optimizes against.

## Deliverables

1. Cost baseline and attribution model.
2. Compute cost optimization (autoscaling, cluster lifecycle, spot VMs).
3. Storage cost optimization (classes, lifecycle, partitioning,
   compression).
4. Scheduling optimization.
5. Rightsizing review process.
6. Budget monitoring and alerts.

## Risks

Cost creep from orphaned resources, over-provisioned clusters, or
un-tiered storage — mitigated by the governance and monitoring already
established in
[`12-cluster-design/06-cluster-policies-and-governance.md`](../12-cluster-design/06-cluster-policies-and-governance.md)
and [`18-monitoring/`](../18-monitoring/README.md), applied here with a
cost-specific lens.

## Rollback

Cost optimization changes (e.g., adjusting an autoscaling policy) are
Terraform-managed and reversible like any other infrastructure change.

## Validation

Actual billing data is reviewed monthly against the cost baseline and
budget — any unexplained variance is investigated, not just noted.

## Best Practices

Attribute cost per data domain from day one (via the labeling standard in
[`13-infrastructure/03-naming-and-tagging-standards.md`](../13-infrastructure/03-naming-and-tagging-standards.md))
— retrofitting cost attribution after the fact is far harder than building
it in from the start.

## Lessons Learned

The single most common cloud cost overrun cause in comparable migrations
is orphaned/idle resources (a cluster that failed to tear down, an
oversized persistent cluster nobody revisited) — not per-unit pricing
surprises.

## Common Mistakes

- Treating cost optimization as a one-time exercise at migration
  completion instead of an ongoing discipline.
- Optimizing cost in ways that compromise Tier 1 SLA reliability (e.g.,
  over-aggressive preemptible usage) without explicit risk acceptance.

## Production Notes

Review cost specifically around the first peak trading season on GCP —
this is both the highest-cost period and the highest-value period to
confirm autoscaling and rightsizing decisions actually hold up under real
peak load.

---

## Folder structure

```
19-cost-optimization/
├── README.md                                     This file
├── 01-cost-baseline-and-attribution.md            Baseline model, per-domain attribution
├── 02-compute-cost-optimization.md                Autoscaling, cluster lifecycle, spot/preemptible
├── 03-storage-cost-optimization.md                Storage classes, lifecycle, partitioning, compression
├── 04-scheduling-optimization.md                  Timing-based cost efficiency
├── 05-rightsizing-review-process.md               Recurring review cadence and process
└── 06-budget-monitoring-and-alerts.md             Tiered budget alerting
```
