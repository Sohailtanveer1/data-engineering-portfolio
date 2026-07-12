# 17 — Performance Tuning

## Purpose

Ensure every migrated job meets or beats its on-prem SLA
([`01-discovery/inventories/01-sla-inventory.md`](../01-discovery/inventories/01-sla-inventory.md))
on Dataproc — re-platforming alone does not guarantee equivalent
performance, and Spark on Dataproc has a genuinely different performance
profile (GCS vs. HDFS I/O characteristics, network topology) that requires
deliberate tuning, not just a lift-and-shift assumption that "cloud is
faster."

## Owner

**Platform Engineering**, per job family, validated in
[`15-testing/08-performance-testing-overview.md`](../15-testing/08-performance-testing-overview.md).

## Inputs

- Performance test results from
  [`15-testing/08-performance-testing-overview.md`](../15-testing/08-performance-testing-overview.md).
- Current on-prem shuffle/I/O characteristics from
  [`03-current-environment/05-storage-and-network-assessment.md`](../03-current-environment/05-storage-and-network-assessment.md).

## Outputs

- Tuned Spark configuration per job family, meeting SLA under
  representative and peak load.
- Documented tuning rationale, reusable across similar future jobs.

## Prerequisites

[`15-testing/`](../15-testing/README.md) providing a performance test
result to tune against; [`12-cluster-design/`](../12-cluster-design/README.md)
providing the baseline cluster configuration being tuned.

## Deliverables

1. Shuffle tuning guidance.
2. Partition tuning guidance.
3. Broadcast join guidance.
4. AQE configuration guidance.
5. Caching strategy.
6. Skew handling guidance.
7. Executor sizing and dynamic allocation guidance.
8. Dataproc-specific tuning (beyond generic Spark tuning).

## Risks

Over-tuning to a single test scenario, producing a configuration that
performs well in testing but poorly under a different real production
load pattern (e.g., tuned for typical-day volume, not tested against peak).

## Rollback

Spark configuration is versioned alongside job code (per
[`07-spark-migration/04-packaging-and-dependency-management.md`](../07-spark-migration/04-packaging-and-dependency-management.md))
— a tuning regression is rolled back the same way any job code change is.

## Validation

Every tuning change is re-validated through
[`15-testing/08-performance-testing-overview.md`](../15-testing/08-performance-testing-overview.md)
before being considered final, not just "should be faster" reasoning.

## Best Practices

Tune with real, representative data volume — a configuration tuned
against a trivially small test dataset frequently doesn't hold at real
production scale, particularly for shuffle and skew-related settings.

## Lessons Learned

The most common Spark-on-cloud performance regression is unaddressed data
skew in a join or aggregation — this was often masked on-prem by simply
throwing more shared cluster capacity at the problem, a workaround that
doesn't exist in the same form on a right-sized ephemeral Dataproc
cluster.

## Common Mistakes

- Assuming Dataproc/GCS will automatically outperform on-prem HDFS without
  tuning, given "it's the cloud."
- Tuning once at migration time and never revisiting as data volume grows
  (per the growth trend data in
  [`03-current-environment/08-resource-utilization-report.md`](../03-current-environment/08-resource-utilization-report.md)).

## Production Notes

Tune every Tier 1 job explicitly against **peak-trading-equivalent**
volume, not just typical-day volume — a job that meets SLA on a normal
Tuesday but not on Black Friday has not actually been validated for the
scenario that matters most.

---

## Folder structure

```
17-performance/
├── README.md                                              This file
├── 01-shuffle-tuning.md
├── 02-partition-tuning.md
├── 03-broadcast-joins.md
├── 04-adaptive-query-execution.md
├── 05-caching-strategy.md
├── 06-skew-handling.md
├── 07-executor-sizing-and-dynamic-allocation.md
└── 08-dataproc-tuning.md
```
