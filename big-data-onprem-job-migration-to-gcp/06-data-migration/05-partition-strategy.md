# Partition Strategy

**Purpose:** Establish a standardized partitioning approach applied
consistently across all migrated tables — replacing whatever inconsistent
conventions may exist on-prem today — to optimize both BigQuery and
Dataproc-Hive query performance and cost.
**Owner:** Data Engineering, with performance validation from
[`17-performance/`](../17-performance/README.md).

---

## Default partitioning standard

| Table Characteristic | Recommended Partition Key | Rationale |
|---|---|---|
| Time-series/event data with a clear date/timestamp column (most tables) | Date (daily) partition on the natural event timestamp | Matches common query pattern (recent data queried most), enables partition pruning, matches existing HDFS `dt=` convention already familiar to the team |
| Very high daily volume tables (e.g., clickstream) | Date + hour partition | Keeps individual partition size manageable for query performance and load parallelism |
| Tables queried primarily by a non-time dimension (e.g., always filtered by region or category) | Consider a secondary clustering key (BigQuery clustering, or Hive bucketing) in addition to date partitioning | Improves pruning for the dominant query filter beyond just date |
| Small reference/lookup tables (under a few GB) | No partitioning needed | Partitioning overhead isn't justified below a certain size threshold |

## BigQuery-specific guidance

- Use **native date/timestamp partitioning** (`PARTITION BY DATE(...)`) —
  not an ingestion-time pseudo-column unless the table genuinely has no
  reliable event-time column.
- Add **clustering** on the 1-4 columns most commonly used in `WHERE`/
  `JOIN` predicates after the partition key (e.g., cluster
  `fraud.txn_feature_scores` by `customer_id` after partitioning by date).
- Set a **partition expiration** aligned with the retention policy from
  [`01-discovery/inventories/04-data-retention-and-compliance.md`](../01-discovery/inventories/04-data-retention-and-compliance.md)
  where legally appropriate, automating compliant data lifecycle
  management rather than relying on a manual cleanup process.

## Dataproc-Hive-specific guidance

- Preserve Hive-style directory partitioning
  (`gs://.../table/dt=2026-07-12/`) for compatibility with existing Spark
  job read patterns and partition-pruning behavior.
- Avoid excessive partition granularity that creates a very high partition
  count — this was already flagged as a Metastore performance concern in
  [`03-current-environment/04-hive-environment-assessment.md`](../03-current-environment/04-hive-environment-assessment.md)
  and should not be reproduced in the migrated target.

## Migrating existing partition schemes

For each table, compare the current on-prem partition scheme (from
[`01-discovery/inventories/09-hive-inventory.md`](../01-discovery/inventories/09-hive-inventory.md))
against this standard:

| Table | Current Partition Scheme | Meets New Standard? | Action |
|---|---|---|---|
| `pricing.daily_price_snapshot` | `dt` (date) | Yes | Carry forward as-is |
| `fraud.txn_feature_scores` | `dt`, `hour` | Yes | Carry forward, add BigQuery clustering on `customer_id` |
| `legacy.vendor_feed_2019_raw` | None | N/A | Retirement candidate — no action needed if not migrated |

_(Populate exhaustively per table.)_

## Common Mistakes

- Applying a uniform daily-partition standard to a table with extremely
  low daily volume, creating many tiny partitions that hurt rather than
  help query performance (BigQuery has per-partition minimum-size
  efficiency considerations) — apply judgment, not a mechanical rule, for
  low-volume tables.
- Choosing a partition key that doesn't match the dominant query filter
  pattern identified in
  [`01-discovery/questions/08-data-consumers.md`](../01-discovery/questions/08-data-consumers.md)
  — partitioning by ingestion date when consumers always filter by a
  business event date produces poor pruning.

## Production Notes

Validate the chosen partition scheme for every Tier 1 table against actual
representative queries in
[`17-performance/`](../17-performance/README.md) before finalizing — a
partition scheme that looks correct on paper should still be benchmarked
against real query patterns before being locked in for a business-critical
table.
