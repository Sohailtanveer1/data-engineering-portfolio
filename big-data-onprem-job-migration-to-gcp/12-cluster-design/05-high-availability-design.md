# High Availability Design (Persistent Clusters)

**Purpose:** Define HA configuration for the small set of persistent
clusters (streaming, interactive) identified in
[`01-cluster-topology-decision.md`](01-cluster-topology-decision.md) —
ephemeral clusters don't need this treatment since their "availability"
model is simply fast, reliable recreation, not uptime.
**Owner:** Platform Engineering.

---

## HA mode for persistent clusters

Dataproc's HA mode runs 3 master nodes (vs. 1 in standard mode), providing
resilience against a single master node failure without cluster downtime
— required for the streaming `fraud_score_hourly`-style cluster given its
Tier 1 criticality and continuous-availability requirement.

```hcl
# Terraform excerpt — see 13-infrastructure/
resource "google_dataproc_cluster" "fraud_streaming_cluster" {
  name = "fraud-streaming-prod"
  cluster_config {
    master_config {
      num_instances = 3   # HA mode
      machine_type  = "n2-standard-8"
    }
    # ... worker config, autoscaling policy reference
  }
}
```

## Comparison against the on-prem single-NameNode SPOF

This directly resolves the specific gap identified in
[`03-current-environment/09-pain-points-and-bottlenecks.md`](../03-current-environment/09-pain-points-and-bottlenecks.md)
pain point #2 for any workload migrated onto a persistent cluster — the
on-prem platform's single, non-HA NameNode is replaced by both HA-mode
Dataproc masters (for the cluster itself) and GCS's inherent durability
(for the underlying storage layer, which has no single point of failure
by construction).

## Multi-zone worker distribution

Persistent cluster workers are distributed across multiple zones within
the region (where Dataproc/the region's zone count supports it), reducing
exposure to a single-zone outage — evaluated against the actual RTO
requirement for the specific workload from
[`01-discovery/inventories/05-disaster-recovery-rpo-rto.md`](../01-discovery/inventories/05-disaster-recovery-rpo-rto.md).

## Recovery procedure

| Failure Scenario | Recovery Behavior |
|---|---|
| Single master failure (HA mode) | Automatic failover to a surviving master; no manual intervention required |
| Full cluster failure (rare, e.g., a broader zonal issue) | Cluster recreated from Terraform-defined configuration; for streaming workloads, the job resumes from its last checkpoint (per the job's own checkpointing design in [`07-spark-migration/`](../07-spark-migration/README.md)) |
| Region-wide outage | Addressed by the broader DR strategy in [`01-discovery/inventories/05-disaster-recovery-rpo-rto.md`](../01-discovery/inventories/05-disaster-recovery-rpo-rto.md) and [`04-target-architecture/04-storage-architecture.md`](../04-target-architecture/04-storage-architecture.md) regional strategy — out of scope for cluster-level HA alone |

## Common Mistakes

- Applying HA mode uniformly to every persistent cluster regardless of
  criticality, adding unnecessary cost for lower-tier persistent workloads
  that could tolerate standard-mode's brief master-failure recovery time.
- Assuming HA mode alone provides full disaster recovery — it protects
  against master node failure specifically, not zone or region-level
  outages, which require the broader DR design.

## Production Notes

Test actual master failover behavior for the `fraud_score_hourly`
persistent cluster (or its equivalent) in a non-production environment
before relying on HA mode in production — confirm failover time and
verify the streaming job resumes correctly without data loss or
duplication, consistent with the idempotency requirement in
[`07-spark-migration/07-idempotency-design.md`](../07-spark-migration/07-idempotency-design.md).
