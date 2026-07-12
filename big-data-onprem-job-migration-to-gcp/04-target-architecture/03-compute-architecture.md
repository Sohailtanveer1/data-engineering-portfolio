# Compute Architecture

**Purpose:** Define the Dataproc cluster patterns this platform uses —
when to use ephemeral vs. persistent clusters, and when (if ever) Dataproc
Serverless is appropriate — directly addressing pain points #1 (fixed
capacity) and #3 (queue contention) from
[`03-current-environment/09-pain-points-and-bottlenecks.md`](../03-current-environment/09-pain-points-and-bottlenecks.md).
Full sizing and configuration detail lives in
[`12-cluster-design/`](../12-cluster-design/README.md); this document
establishes the pattern-level decisions that sizing builds on.
**Owner:** Platform Engineering + Cloud/DevOps.

---

## Compute pattern decision framework

| Workload Characteristic | Recommended Pattern | Why |
|---|---|---|
| Scheduled batch job, runs once or a few times daily, well-defined resource needs | **Ephemeral Dataproc cluster**, created via Composer at job start, torn down at job end | No idle cost; no queue contention with other jobs; resource footprint tuned per job |
| Streaming/near-continuous job (e.g., fraud scoring) | **Long-running (persistent) Dataproc cluster**, sized for sustained load, or Dataproc on GKE for finer-grained scaling | Ephemeral start/stop overhead is incompatible with continuous/low-latency processing |
| Ad-hoc/interactive analyst queries | **Persistent Dataproc cluster** (or migrate the workload to BigQuery, see [`05-data-warehouse-architecture.md`](05-data-warehouse-architecture.md)) | Interactive workloads need low-latency availability; evaluate whether BigQuery serves this better than Dataproc at all |
| Highly variable, unpredictable-schedule batch (e.g., backfills, reprocessing) | **Dataproc Serverless for Spark**, if the job's dependencies are compatible | No cluster management overhead at all; pay only for actual Spark execution; best fit for irregular workloads |
| Jobs sharing a tightly-coupled workflow (multiple steps in one Oozie bundle) | **Ephemeral cluster per workflow run**, shared across the workflow's steps, torn down after the full workflow completes | Avoids repeated cluster startup overhead within a single logical run while still avoiding persistent idle cost |

## Why ephemeral-by-default resolves the current pain points

On-prem, all workloads compete for a shared, fixed-capacity YARN cluster
(see
[`03-current-environment/02-yarn-resource-assessment.md`](../03-current-environment/02-yarn-resource-assessment.md)).
This produces exactly the two dominant pain points identified: capacity
that's either insufficient (peak) or wasted (off-peak), and queue
contention causing job delays. Ephemeral, per-job Dataproc clusters
eliminate both by construction — each job gets exactly the capacity it
needs, for exactly the duration it needs it, without contending with any
other job's allocation.

## Cluster creation and teardown pattern

- Clusters are created via Terraform-defined Dataproc cluster
  configurations, parameterized per job family (see
  [`13-infrastructure/`](../13-infrastructure/README.md) for the reusable
  Terraform module), and triggered from Cloud Composer using the
  `DataprocCreateClusterOperator` / `DataprocSubmitJobOperator` /
  `DataprocDeleteClusterOperator` sequence — see
  [`09-composer-migration/`](../09-composer-migration/README.md) for DAG
  patterns.
- Cluster configuration (machine types, initial worker count, autoscaling
  policy) is defined per job family based on the resource footprint data
  captured in
  [`01-discovery/inventories/08-spark-inventory.md`](../01-discovery/inventories/08-spark-inventory.md),
  not a single one-size-fits-all template.
- Failed cluster creation or job failure triggers explicit cleanup (cluster
  deletion) even on failure paths — a stuck, un-deleted cluster is a direct
  cost leak, addressed explicitly in
  [`19-cost-optimization/`](../19-cost-optimization/README.md).

## Autoscaling

Dataproc autoscaling policies (for the smaller number of persistent
clusters that do exist, e.g., the interactive/ad-hoc cluster) are
configured based on the queue contention and utilization data in
[`03-current-environment/02-yarn-resource-assessment.md`](../03-current-environment/02-yarn-resource-assessment.md)
and [`03-current-environment/08-resource-utilization-report.md`](../03-current-environment/08-resource-utilization-report.md).
Detailed policy configuration is in
[`12-cluster-design/`](../12-cluster-design/README.md).

## When NOT to use ephemeral clusters

Ephemeral clusters are the default, not a universal rule. Exceptions,
explicitly justified:

- **Streaming workloads** (continuous, not batch) — cluster startup
  latency (typically 90 seconds to a few minutes) is incompatible with
  low-latency continuous processing.
- **Very short, very frequent jobs** where cluster startup overhead would
  dominate total runtime — evaluate Dataproc Serverless or a shared
  persistent cluster for these instead.
- **Workloads requiring warm caching/state between runs** that can't be
  cheaply rehydrated from GCS on every cluster creation.

## Common Mistakes

- Defaulting every workload to a persistent cluster "to keep it simple" —
  this reproduces the current platform's fixed-capacity cost and
  contention problems on GCP instead of resolving them.
- Sizing ephemeral cluster configurations from guesswork instead of the
  measured resource footprint in
  [`01-discovery/inventories/08-spark-inventory.md`](../01-discovery/inventories/08-spark-inventory.md)
  — an ephemeral cluster that's badly undersized just moves the queue-
  contention pain point from YARN scheduling to repeated OOM/retry cycles.

## Production Notes

Tier 1 job clusters (pricing, fraud, inventory, finance) should have
autoscaling policies explicitly tested against peak-trading-equivalent
load in [`15-testing/`](../15-testing/README.md) and
[`17-performance/`](../17-performance/README.md) before their cutover wave
— an autoscaling policy that works at steady-state load but fails to scale
fast enough during a traffic spike is a direct production risk.
