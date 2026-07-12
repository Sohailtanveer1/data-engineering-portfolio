# Storage & Network Assessment (Infrastructure Layer)

**Purpose:** Document the physical/infrastructure characteristics of
storage and networking within and around the cluster — disk layout, I/O
characteristics, and intra-cluster network topology — as distinct from the
data-content-focused storage inventory in
[`01-discovery/inventories/11-storage-inventory.md`](../01-discovery/inventories/11-storage-inventory.md)
and the connectivity-requirements-focused
[`01-discovery/questions/04-networking-team.md`](../01-discovery/questions/04-networking-team.md).
This document answers "how is the infrastructure built," feeding
[`12-cluster-design/`](../12-cluster-design/README.md) and
[`11-network/`](../11-network/README.md).
**Owner:** Platform Engineering, with Network Engineering input.

---

## Storage layer

| Metric | Value |
|---|---|
| Disk type per DataNode | _(HDD / SSD / mixed tiers)_ |
| Disks per DataNode | |
| RAID configuration (if any) | _(commonly JBOD for HDFS)_ |
| Local disk I/O observed as a bottleneck? | _(yes/no, evidence)_ |
| HDFS short-circuit reads enabled? | |
| Any tiered storage in use (hot/warm/cold, HDFS storage policies)? | |

## Intra-cluster network

| Metric | Value |
|---|---|
| Network fabric (1GbE / 10GbE / 25GbE / other) | |
| Rack topology and rack-awareness configuration | |
| Known network bottlenecks (e.g., cross-rack shuffle contention) | |
| Network utilization during peak batch windows | |

## Shuffle and I/O characteristics

| Question | Finding |
|---|---|
| Are Spark jobs commonly shuffle-bound (network/disk heavy during shuffle phases)? | |
| Is there evidence of disk contention during concurrent job execution? | |
| Are there known "noisy neighbor" effects between jobs sharing the same nodes? | |

This data directly informs whether GCS (object storage, not a local disk
equivalent) plus Dataproc's typical persistent-disk-backed shuffle changes
the performance profile favorably or requires specific tuning attention in
[`17-performance/`](../17-performance/README.md) — e.g., evaluating
Dataproc's enhanced flexibility mode or SSD-backed shuffle for
shuffle-heavy Tier 1 jobs.

## Edge/gateway node network access

| Edge Node | Network Zones Reachable | External System Access (per [`01-discovery/inventories/12-external-dependencies.md`](../01-discovery/inventories/12-external-dependencies.md)) |
|---|---|---|
| | | |

This confirms which specific network paths
[`11-network/`](../11-network/README.md) must replicate for the GCP
platform to keep reaching the same external systems.

## Common Mistakes

- Treating "storage" only as an HDFS capacity question and skipping local
  disk I/O characteristics, which materially affect Spark shuffle
  performance and therefore the performance-parity conversation in
  [`17-performance/`](../17-performance/README.md).
- Assuming intra-cluster network topology is irrelevant to a cloud
  migration — it's the baseline against which GCS latency/throughput
  characteristics (object storage, not local disk) must be evaluated,
  since the performance model genuinely differs.

## Production Notes

If shuffle-bound performance issues are identified for any Tier 1 job,
flag this explicitly as a required focus area for
[`17-performance/`](../17-performance/README.md) tuning validation before
that job's cutover — do not assume Dataproc will "just be faster."
