# Performance Testing Overview

**Purpose:** Define the performance testing **process and gates** —
detailed tuning techniques (shuffle, partitioning, broadcast joins, AQE,
skew handling) live in
[`17-performance/`](../17-performance/README.md); this document defines
when and how performance is tested as part of the overall test strategy.
**Owner:** Platform Engineering, run in `stage`.

---

## Performance testing gate

Every Tier 1/2 job must pass a performance test — running against
representative (ideally peak-equivalent) data volume and confirming
completion within its documented SLA
([`01-discovery/inventories/01-sla-inventory.md`](../01-discovery/inventories/01-sla-inventory.md))
— before proceeding to
[`14-job-migration/07-production-deployment-checklist.md`](../14-job-migration/07-production-deployment-checklist.md).

## Test data volume requirements

| Tier | Required Test Data Volume |
|---|---|
| Tier 1 | Full production-representative volume, ideally including a sample from the last peak trading event |
| Tier 2 | At least 50% of typical production volume, scaled/extrapolated for full-volume SLA projection |
| Tier 3 | Representative sample sufficient to catch obvious performance issues; full SLA validation not required |

## Process

1. Load representative test data into `stage` (per
   [`06-data-migration/`](../06-data-migration/README.md) patterns, using
   masked/sampled real data or synthetic data matching real data
   characteristics — never a trivially small, unrepresentative test set).
2. Run the job under its actual target Dataproc cluster configuration
   (per [`12-cluster-design/`](../12-cluster-design/README.md)) — not a
   scaled-down "test" configuration that wouldn't reflect real production
   performance.
3. Measure end-to-end duration, resource utilization, and any bottleneck
   indicators (shuffle spill, skew, executor idle time).
4. Compare against the SLA target; if not met, apply tuning per
   [`17-performance/`](../17-performance/README.md) and re-test.
5. Record final validated performance in the job's entry in
   [`14-job-migration/03-migration-tracker.md`](../14-job-migration/03-migration-tracker.md).

## Common Mistakes

- Performance-testing against a small, non-representative dataset and
  extrapolating linearly to full volume — Spark performance
  characteristics (shuffle behavior, skew impact) frequently don't scale
  linearly, making this extrapolation unreliable.
- Treating a single passing performance test run as sufficient — run at
  least 2-3 times to confirm consistency, since cloud resource performance
  can have run-to-run variance.

## Production Notes

For Tier 1 jobs, performance test data should specifically include the
data shape/volume from the last peak trading event if available (per
[`03-current-environment/08-resource-utilization-report.md`](../03-current-environment/08-resource-utilization-report.md))
— a job performance-tested only against typical-day volume has not
actually validated the scenario that matters most for an ecommerce
platform.
