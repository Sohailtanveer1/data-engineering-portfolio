# Statistics Migration

**Purpose:** Ensure table and column statistics are current in the target
platform — required for good query planning/performance in both
Dataproc-Hive (cost-based optimizer) and BigQuery, and easy to overlook
since "the data is the same" doesn't mean "the statistics carried over."
**Owner:** Data Engineering, validated by
[`17-performance/`](../17-performance/README.md).

---

## Why statistics don't migrate automatically

Hive/Spark's cost-based optimizer and BigQuery's query planner both rely on
table/column statistics (row counts, NDV — number of distinct values,
min/max, null counts) to choose efficient execution plans (e.g., join
ordering, broadcast vs. shuffle join decisions). These statistics are
computed and stored separately from the data itself and are **not**
carried over by a storage-level data copy — they must be explicitly
recomputed against the migrated data.

## Recomputing statistics — Dataproc-Hive

```sql
ANALYZE TABLE pricing.daily_price_snapshot COMPUTE STATISTICS;
ANALYZE TABLE pricing.daily_price_snapshot COMPUTE STATISTICS FOR COLUMNS;
```

Run this after partition registration
([`03-partition-migration.md`](03-partition-migration.md)) is complete for
a table, and re-run it after any significant incremental load, per a
scheduled maintenance cadence defined alongside
[`09-composer-migration/`](../09-composer-migration/README.md) DAG design
(e.g., a periodic `ANALYZE TABLE` DAG task, not a one-time migration-only
step).

## Statistics in BigQuery

BigQuery automatically maintains its own internal statistics for native
tables and generally requires no manual `ANALYZE`-equivalent step — confirm
this is functioning as expected during
[`17-performance/`](../17-performance/README.md) validation rather than
assuming zero action is needed, since query performance is still worth
explicitly verifying post-migration regardless of the underlying
mechanism.

## Validation

| Check | Method |
|---|---|
| Statistics exist and are non-stale for every migrated Dataproc-Hive table | `DESCRIBE FORMATTED <table>` shows recent statistics timestamp and non-zero row count |
| Query plans use statistics-informed decisions (e.g., broadcast join chosen for a small table) | `EXPLAIN` a representative query and confirm the plan looks reasonable, cross-checked in [`17-performance/`](../17-performance/README.md) |

## Common Mistakes

- Migrating a table's data and DDL but forgetting the `ANALYZE TABLE` step
  entirely — the table works correctly (correct data) but performs poorly
  (bad query plans from missing/default statistics), which can be
  mistakenly attributed to "Dataproc is just slower" rather than the real,
  fixable cause.
- Computing statistics once at migration time and never refreshing them as
  the table grows via incremental loads — stale statistics degrade query
  planning over time even for a correctly-migrated table.

## Production Notes

For Tier 1 tables, verify query plan quality explicitly (via `EXPLAIN`
comparison against representative queries) as part of
[`17-performance/`](../17-performance/README.md) validation before that
table's job cutover — a performance regression traced back to missing
statistics is an easily preventable, easily fixed issue if caught before
cutover, and a confusing, harder-to-diagnose one if discovered after.
