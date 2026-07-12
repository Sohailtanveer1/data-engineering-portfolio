# Cluster Topology Decision (Per Job Family)

**Purpose:** Apply the compute pattern decision framework from
[`04-target-architecture/03-compute-architecture.md`](../04-target-architecture/03-compute-architecture.md)
concretely, per job family, from the actual job inventory.
**Owner:** Platform Engineering.

---

## Job family → topology mapping

| Job Family | Representative Jobs | Topology | Rationale |
|---|---|---|---|
| Nightly/scheduled batch (most jobs) | `pricing_nightly_batch`, `finance_gl_reconciliation` | Ephemeral, created per run | No idle cost, no contention, sized per family |
| Intraday/near-continuous | `inventory_sync_intraday` (every 15 min) | Ephemeral, but evaluate cluster startup overhead vs. run frequency — if 15-min cadence makes ephemeral startup overhead proportionally too costly, consider a persistent small cluster instead | Frequency-dependent — validate actual startup-to-runtime ratio before deciding |
| Streaming | `fraud_score_hourly` (Structured Streaming) | Persistent | Continuous processing incompatible with ephemeral start/stop cycles |
| Ad-hoc/interactive analyst queries | Analyst notebook sessions | Persistent (or evaluate BigQuery migration per [`04-target-architecture/05-data-warehouse-architecture.md`](../04-target-architecture/05-data-warehouse-architecture.md)) | Interactive workloads need low-latency availability |
| Irregular backfill/reprocessing | Ad-hoc historical reprocessing jobs | Dataproc Serverless | No predictable schedule; serverless avoids idle cluster management for infrequent, unpredictable-timing work |

## Deciding the intraday-frequency edge case

For `inventory_sync_intraday`-style jobs (very frequent, moderate
duration), explicitly calculate:

```
startup_overhead_ratio = cluster_startup_time / job_run_duration
```

If this ratio exceeds roughly 20-30% of total run time, the overhead of
repeated ephemeral cluster creation becomes a material inefficiency —
evaluate a small, always-on persistent cluster instead, sized minimally
and monitored for utilization to confirm it's not sitting idle most of the
time (which would undercut the cost benefit versus ephemeral).

## Per-family cluster template ownership

Each job family's cluster configuration is defined **once**, as a
Terraform module input (per
[`13-infrastructure/`](../13-infrastructure/README.md)), and referenced by
every job in that family's Composer DAG — never hand-tuned per individual
job run, consistent with the standardization principle in
[`07-spark-migration/03-dataproc-submission-patterns.md`](../07-spark-migration/03-dataproc-submission-patterns.md).

## Common Mistakes

- Defaulting every job to ephemeral without checking the startup-overhead
  ratio for very frequent jobs, silently degrading efficiency for exactly
  the jobs where it matters most.
- Creating a persistent cluster for a streaming job but never right-sizing
  it against actual sustained load, leaving it either overprovisioned
  (wasting cost) or underprovisioned (risking Tier 1 SLA).

## Production Notes

Re-evaluate the topology decision for `inventory_sync_intraday` and any
other high-frequency job specifically using real measured Dataproc cluster
startup times (not vendor-quoted averages) from
[`15-testing/`](../15-testing/README.md) before finalizing.
