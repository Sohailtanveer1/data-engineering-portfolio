# Shuffle Tuning

**Purpose:** Shuffle is the most common Spark performance bottleneck, and
its cost profile changes meaningfully moving from HDFS-local-disk-backed
shuffle on-prem to GCS-object-storage-backed processing on Dataproc.
**Owner:** Platform Engineering.

---

## Why shuffle behaves differently on Dataproc

On-prem, Spark shuffle writes to local HDFS-backed disk with fast,
consistent local I/O. On Dataproc, shuffle by default still uses local
worker disk (not GCS directly) — but the elasticity of ephemeral,
autoscaled clusters means shuffle data can be lost if a worker is scaled
down or preempted mid-shuffle, a behavior difference from a stable
on-prem cluster that must be explicitly accounted for.

## Key configuration

| Setting | Guidance |
|---|---|
| `spark.sql.shuffle.partitions` | Don't rely on the static default (200); either let AQE's `coalescePartitions` manage this dynamically (recommended, see [`04-adaptive-query-execution.md`](04-adaptive-query-execution.md)) or size explicitly based on data volume — a rough starting heuristic is 2-3x the total core count of the cluster |
| Dataproc Enhanced Flexibility Mode (EFM) | For clusters using preemptible/secondary workers (per [`12-cluster-design/04-preemptible-and-spot-strategy.md`](../12-cluster-design/04-preemptible-and-spot-strategy.md)), enable EFM's shuffle service to avoid shuffle data loss when a secondary worker is reclaimed mid-job |
| `spark.shuffle.service.enabled` | Enabled, working with EFM to decouple shuffle data from individual executor lifecycle |
| Local SSD for shuffle-heavy job families | For job families identified as shuffle-heavy in [`03-current-environment/05-storage-and-network-assessment.md`](../03-current-environment/05-storage-and-network-assessment.md), attach local SSDs to worker nodes (per [`12-cluster-design/02-node-sizing-and-machine-types.md`](../12-cluster-design/02-node-sizing-and-machine-types.md)) rather than relying on standard persistent disk |

## Diagnosing shuffle issues

Use the Spark UI (accessible via the Dataproc cluster's web interfaces, or
the persistent Spark History Server per
[`18-monitoring/`](../18-monitoring/README.md)) to check:

- **Shuffle read/write size** per stage — disproportionately large shuffle
  relative to input data size indicates an opportunity for broadcast join
  conversion (per [`03-broadcast-joins.md`](03-broadcast-joins.md)) or
  filter pushdown earlier in the pipeline.
- **Shuffle spill** (data spilling to disk due to insufficient executor
  memory) — indicates executor memory is undersized for the shuffle
  volume, requiring either more executor memory or better partitioning.

## Common Mistakes

- Leaving `spark.sql.shuffle.partitions` at its static default of 200
  regardless of actual data volume — either far too many small partitions
  for a small job (overhead-dominated) or far too few for a large job
  (each partition too large, causing spill).
- Not enabling Enhanced Flexibility Mode for clusters with preemptible
  workers, risking shuffle data loss and expensive task retries exactly
  when preemption occurs.

## Production Notes

For the illustrative `pricing_nightly_batch` job (flagged as shuffle-heavy
in
[`03-current-environment/05-storage-and-network-assessment.md`](../03-current-environment/05-storage-and-network-assessment.md)),
validate EFM and local SSD configuration explicitly under
[`15-testing/08-performance-testing-overview.md`](../15-testing/08-performance-testing-overview.md)
peak-volume testing before its production cutover — shuffle issues often
only manifest clearly at real data scale.
