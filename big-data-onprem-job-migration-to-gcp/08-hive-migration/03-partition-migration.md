# Partition Migration

**Purpose:** Ensure every partition's metadata is correctly registered in
the target catalog (Dataproc Metastore or BigQuery), not just the
underlying data files — a common gap since data can be present in GCS
while the catalog is unaware of it, making it invisible to queries.
**Owner:** Data Engineering.

---

## Why partition metadata migration is a distinct step

Copying partitioned data files to GCS (per
[`05-storage-migration/`](../05-storage-migration/README.md)) does not
automatically register those partitions in a new Metastore or BigQuery
table — partition discovery must be explicitly triggered, or partition
metadata explicitly created, matching the partition scheme decided in
[`06-data-migration/05-partition-strategy.md`](../06-data-migration/05-partition-strategy.md).

## Dataproc-Hive (Metastore) partition registration

```sql
-- After data files exist at the correct GCS paths, register partitions
-- either individually (for a small, known set) or via discovery:
MSCK REPAIR TABLE pricing.daily_price_snapshot;
```

`MSCK REPAIR TABLE` scans the table's GCS location for partition-shaped
subdirectories (`dt=.../`) and registers any not already known to the
Metastore. For very large partition counts, prefer batched, explicit
`ALTER TABLE ... ADD PARTITION` statements generated programmatically
from the known migration batch list (from
[`06-data-migration/01-historical-data-migration-plan.md`](../06-data-migration/01-historical-data-migration-plan.md))
rather than a full `MSCK REPAIR`, which can be slow and resource-intensive
against a very large table.

## BigQuery partition registration

For native BigQuery tables using date/timestamp partitioning, partitions
are created automatically as data is loaded (via `bq load` or a Spark
BigQuery connector write) — no separate registration step is needed,
provided the load job correctly targets the partitioned table with the
partition column populated. Confirm this behavior explicitly during
[`06-data-migration/08-migration-execution-runbook.md`](../06-data-migration/08-migration-execution-runbook.md)
execution rather than assuming it.

## Partition count validation

After registration, validate the partition count in the target matches
the expected count from the source:

```sql
-- Dataproc-Hive
SHOW PARTITIONS pricing.daily_price_snapshot;

-- BigQuery
SELECT partition_id, total_rows
FROM `project.dataset.INFORMATION_SCHEMA.PARTITIONS`
WHERE table_name = 'daily_price_snapshot';
```

Compare the resulting count against the source Hive table's partition
count (from
[`01-discovery/inventories/09-hive-inventory.md`](../01-discovery/inventories/09-hive-inventory.md))
as part of
[`06-data-migration/07-data-reconciliation-framework.md`](../06-data-migration/07-data-reconciliation-framework.md)
reconciliation — a missing partition is a silent data-availability gap
that won't error, it will simply make that partition's data invisible to
queries.

## Common Mistakes

- Assuming data present in GCS means the data is queryable — without
  partition registration, a query against the target table will silently
  return incomplete results (missing the unregistered partitions) with no
  error.
- Running `MSCK REPAIR TABLE` against a very large table repeatedly during
  incremental backfill instead of using targeted `ADD PARTITION`
  statements for just the newly-added partitions — this wastes
  significant time re-scanning already-registered partitions.

## Production Notes

For Tier 1 tables, partition count validation is a mandatory,
automatically-checked step in
[`06-data-migration/07-data-reconciliation-framework.md`](../06-data-migration/07-data-reconciliation-framework.md)
— never rely on a manual spot-check alone, since a missing partition
produces no error, only silently incomplete query results that could go
unnoticed until a business user asks why a report is missing data.
