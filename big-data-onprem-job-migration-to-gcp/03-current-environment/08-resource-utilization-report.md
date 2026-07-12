# Resource Utilization Report

**Purpose:** Provide measured (not estimated) resource utilization data —
CPU, memory, storage, network — over a representative period **including
peak trading load**, as the primary sizing input for
[`12-cluster-design/`](../12-cluster-design/README.md) and the cost
baseline for [`19-cost-optimization/`](../19-cost-optimization/README.md).
**Owner:** Platform Engineering.
**Inputs:** Cluster monitoring system (Ambari/Cloudera Manager metrics,
Ganglia, or equivalent) covering a minimum 90-day trailing window.
**Validation method:** Utilization figures here must be pulled from the
monitoring system's raw time-series data, not summary dashboards alone —
summary dashboards often default to averages that hide the peak values
that actually matter for sizing.

---

## Reporting window

| Field | Value |
|---|---|
| Reporting window start/end | |
| Includes a peak trading event? (Yes/No — which one) | |
| Includes a month-end/quarter-end close period? | |
| Data source (monitoring system name/version) | |

If the reporting window does **not** include a peak trading event, this
must be explicitly flagged as a known gap, with a plan to backfill peak-day
utilization data from historical monitoring archives (if retained) before
[`12-cluster-design/`](../12-cluster-design/README.md) finalizes sizing.

## Cluster-wide utilization

| Metric | P50 (typical) | P95 | Peak observed (date) | Peak trading event value (if captured) |
|---|---|---|---|---|
| CPU utilization (%) | | | | |
| Memory utilization (%) | | | | |
| HDFS capacity utilization (%) | | | | |
| Network throughput | | | | |
| YARN pending container count | | | | |
| Concurrent running applications | | | | |

## Utilization by workload category

| Workload Category | % of Total Compute Consumed | Peak Concurrency | Notes |
|---|---|---|---|
| Nightly batch (pricing, inventory, finance) | | | |
| Intraday/streaming (fraud, inventory sync) | | | |
| Ad-hoc/interactive queries | | | |
| Backfill/reprocessing (irregular) | | | |

This breakdown is a direct input to the ephemeral-cluster-per-workload
design decision in [`12-cluster-design/`](../12-cluster-design/README.md)
— workload categories with distinct utilization patterns are strong
candidates for separate, independently-autoscaled Dataproc cluster
configurations rather than one shared pool.

## Growth trend

| Metric | 6 months ago | Today | Projected in 12 months (linear extrapolation) |
|---|---|---|---|
| HDFS capacity used | | | |
| Total job count | | | |
| Peak concurrent YARN applications | | | |

Growth trend data should be cross-checked against
[`01-discovery/inventories/11-storage-inventory.md`](../01-discovery/inventories/11-storage-inventory.md)
growth-rate figures for consistency, and used in
[`19-cost-optimization/`](../19-cost-optimization/README.md) to project
GCP cost trajectory, not just a point-in-time snapshot.

## Common Mistakes

- Reporting only average utilization, which systematically understates the
  peak capacity actually required — a cluster averaging 40% CPU
  utilization can still regularly spike to 95%+ during nightly batch
  windows, and sizing to the average produces an under-provisioned target.
- Excluding ad-hoc/interactive query load from the utilization breakdown
  because it's "not a scheduled job" — interactive load still consumes
  real capacity and must be accounted for in sizing.

## Production Notes

If the trailing 90-day window doesn't capture the last Black Friday/Cyber
Monday, pull archived monitoring data from that specific period
separately, even if older than 90 days — peak-trading utilization is
non-negotiable input data for a platform serving an ecommerce business,
and its absence should block, not just caveat,
[`12-cluster-design/`](../12-cluster-design/README.md) sign-off for Tier 1
workload sizing.
