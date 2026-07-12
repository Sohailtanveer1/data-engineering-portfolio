# Rightsizing Review Process

**Purpose:** Establish a recurring, disciplined process for revisiting
cluster and storage sizing based on real GCP operational data — cost
optimization is not a one-time migration activity.
**Owner:** Platform Engineering.

---

## Review cadence

| Review | Frequency | Scope |
|---|---|---|
| Per-job-family compute rightsizing | Monthly during migration program; quarterly in steady state | Compare actual observed executor/memory/duration metrics (per [`18-monitoring/02-metrics-and-dashboards.md`](../18-monitoring/02-metrics-and-dashboards.md)) against current cluster configuration |
| Storage class/lifecycle review | Quarterly | Confirm actual access patterns match configured lifecycle rules |
| Preemptible/spot cap review | After each peak trading season | Adjust caps based on observed preemption impact |
| Committed Use Discount evaluation | Annually, once patterns are stable | Evaluate locking in discounted pricing for confirmed-stable persistent workloads |

## Rightsizing review process

1. Pull actual utilization data for the review period (per
   [`18-monitoring/02-metrics-and-dashboards.md`](../18-monitoring/02-metrics-and-dashboards.md)).
2. Compare against current cluster configuration
   ([`12-cluster-design/02-node-sizing-and-machine-types.md`](../12-cluster-design/02-node-sizing-and-machine-types.md)).
3. Identify over-provisioned (consistently low utilization) or
   under-provisioned (frequent scale-to-max, spill, or SLA-risk) job
   families.
4. Propose a sizing adjustment, validate in `stage` via
   [`15-testing/08-performance-testing-overview.md`](../15-testing/08-performance-testing-overview.md)
   before applying to `prod`.
5. Apply via the standard Terraform environment promotion process (per
   [`13-infrastructure/05-environment-promotion.md`](../13-infrastructure/05-environment-promotion.md)).
6. Track before/after cost and performance impact.

## What triggers an out-of-cycle review

- A sustained cost anomaly detected via
  [`06-budget-monitoring-and-alerts.md`](06-budget-monitoring-and-alerts.md).
- A sustained performance issue suggesting under-provisioning.
- A material change in data volume (per the growth trend tracking from
  [`03-current-environment/08-resource-utilization-report.md`](../03-current-environment/08-resource-utilization-report.md)).

## Common Mistakes

- Rightsizing based on a short observation window that doesn't capture
  normal variability (e.g., basing a permanent downsize decision on one
  unusually quiet week).
- Treating rightsizing as purely a cost-reduction exercise — sometimes
  the review reveals under-provisioning risking SLA, and rightsizing means
  *increasing* capacity, not just decreasing it.

## Production Notes

The first rightsizing review for any Tier 1 job family should happen no
later than 60 days after that family's production cutover — early enough
to catch obvious mis-sizing while the migration context is still fresh in
the team's memory, without being so early that the observation window is
too short to be meaningful.
