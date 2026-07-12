# Storage Cost Optimization

**Purpose:** Apply cost discipline to the GCS storage layer — storage
class lifecycle, partitioning efficiency, and compression — building on
the zoning model in
[`04-target-architecture/04-storage-architecture.md`](../04-target-architecture/04-storage-architecture.md).
**Owner:** Platform Engineering / Data Engineering.

---

## Storage class lifecycle automation

```hcl
# Terraform excerpt — see 13-infrastructure/
resource "google_storage_bucket" "pricing_curated" {
  name = "acme-prod-pricing-curated"
  lifecycle_rule {
    condition { age = 90 }
    action    { type = "SetStorageClass", storage_class = "NEARLINE" }
  }
  lifecycle_rule {
    condition { age = 365 }
    action    { type = "SetStorageClass", storage_class = "COLDLINE" }
  }
  lifecycle_rule {
    condition { age = 2555 }  # 7 years, per retention policy
    action    { type = "Delete" }
  }
}
```

Lifecycle rules are set **per data domain**, matched to the actual
retention and access pattern from
[`01-discovery/inventories/04-data-retention-and-compliance.md`](../01-discovery/inventories/04-data-retention-and-compliance.md)
— not a single platform-wide default, since access patterns and
retention requirements differ meaningfully by domain (e.g., `clickstream`
data's 13-month active window vs. `finance`'s 7-year retention).

## Partitioning and small-file cost impact

Per
[`17-performance/02-partition-tuning.md`](../17-performance/02-partition-tuning.md),
avoiding the small-files problem isn't just a performance concern —
every GCS operation (list, read) has a per-request cost component, and
excessive small files multiply request count disproportionately to actual
data volume. Coalescing output files appropriately is a direct,
measurable cost optimization, not just a performance one.

## Compression cost tradeoff

Per
[`06-data-migration/06-format-and-compression-strategy.md`](../06-data-migration/06-format-and-compression-strategy.md),
the choice between Snappy (faster, larger) and Zstandard (slower, smaller)
compression is a direct storage-cost-vs-compute-cost tradeoff — for
archive-zone data specifically (rarely read, stored long-term), the
storage cost savings from better compression (zstd) outweigh the marginal
compute cost of slower decompression on the rare read.

## Eliminating redundant copies

- **Migration-era snapshots** (per
  [`06-data-migration/04-snapshot-strategy.md`](../06-data-migration/04-snapshot-strategy.md))
  must be cleaned up after their retention window per that document's
  guidance — an accumulating pile of unused migration snapshots is pure
  cost waste.
- **Scratch/temp data** (per
  [`04-target-architecture/04-storage-architecture.md`](../04-target-architecture/04-storage-architecture.md))
  has an aggressive short lifecycle by design — confirm it's actually
  being enforced, not just configured.

## Common Mistakes

- Applying a single storage lifecycle policy uniformly across all data
  domains regardless of actual access pattern, either prematurely
  archiving frequently-accessed data (hurting performance) or failing to
  archive rarely-accessed data (wasting cost).
- Forgetting to clean up migration-era artifacts (snapshots, parallel-run
  duplicate copies) once they're no longer needed, letting them silently
  accumulate cost indefinitely.

## Production Notes

Audit actual storage class distribution and access patterns per domain
quarterly — confirm data is transitioning to cheaper storage classes as
intended and that no frequently-accessed data has been mistakenly
archived, which would hurt performance for an active job.
