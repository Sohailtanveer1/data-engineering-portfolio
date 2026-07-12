# Node Sizing & Machine Types

**Purpose:** Size master and worker nodes per job family using measured
resource footprint data, not defaults.
**Owner:** Platform Engineering.

---

## Master node sizing

| Cluster Type | Master Configuration | Rationale |
|---|---|---|
| Ephemeral, single-job clusters | 1 master, `n2-standard-4` (4 vCPU / 16GB) | Master overhead is minimal for a single-job ephemeral cluster; no HA needed since the whole cluster is disposable and job-scoped |
| Persistent clusters (streaming, interactive) | 3 masters (HA mode), sized per [`05-high-availability-design.md`](05-high-availability-design.md) | Persistent clusters warrant HA given their longer-lived, shared nature |

## Worker sizing per job family

Derived directly from
[`01-discovery/inventories/08-spark-inventory.md`](../01-discovery/inventories/08-spark-inventory.md)
per-job executor/memory data:

| Job Family | On-Prem Executor Profile (P95) | Target Worker Machine Type | Initial Worker Count |
|---|---|---|---|
| `pricing_nightly_batch` | 40 executors × 8g mem | `n2-standard-16` (16 vCPU / 64GB) | 6 (sized to comfortably host peak executor concurrency with headroom) |
| `fraud_score_hourly` (streaming) | 20 executors × 6g mem, continuous | `n2-highmem-8` (8 vCPU / 64GB) — memory-optimized given the streaming state footprint | 4, persistent |
| `inventory_sync_intraday` | 15 executors × 4g mem | `n2-standard-8` | 3 |

_(Illustrative — derive from the actual per-job data in the Spark
inventory, not these example values.)_

## Machine family selection guidance

| Workload Characteristic | Recommended Machine Family |
|---|---|
| General-purpose batch, balanced CPU/memory need | N2 standard |
| Memory-intensive (large joins, wide aggregations, streaming state) | N2 highmem |
| CPU-intensive (heavy computation, light data volume per task) | N2 highcpu or C2 |
| Cost-sensitive, latency-tolerant, interruption-tolerant workloads | Consider E2 for lower cost where sustained peak performance isn't critical |

## Disk sizing

- **Boot disk**: minimal (standard default), since job code and
  dependencies are fetched from GCS/Artifact Registry at job start, not
  baked into a large boot image (except where a custom image is used, per
  [`07-initialization-actions-and-custom-images.md`](07-initialization-actions-and-custom-images.md)).
- **Worker local/shuffle disk**: sized based on the shuffle-heaviness
  characteristics identified in
  [`03-current-environment/05-storage-and-network-assessment.md`](../03-current-environment/05-storage-and-network-assessment.md)
  — shuffle-heavy jobs (per Discovery findings) warrant SSD persistent
  disks or Dataproc's enhanced flexibility mode for shuffle, validated in
  [`17-performance/`](../17-performance/README.md).

## Common Mistakes

- Using a single "standard" machine type across all job families
  regardless of their actual memory/CPU profile, forcing memory-intensive
  jobs into an ill-fitting general-purpose shape.
- Sizing worker count to exactly match P50 executor count instead of P95,
  leaving no headroom for normal variance and forcing autoscaling to
  react from a chronically under-provisioned baseline.

## Production Notes

Validate every Tier 1 job family's sizing against actual peak-trading-day
executor/memory usage where that data exists (per
[`03-current-environment/08-resource-utilization-report.md`](../03-current-environment/08-resource-utilization-report.md)),
not just typical-day P95 — peak trading load may exceed even the typical
P95 profile.
