# External vs. Managed Table Migration

**Purpose:** Handle the distinct migration procedures required for Hive
external tables (data lives independently of the table definition) versus
managed tables (Hive owns the data lifecycle) — a mismatch here causes
either orphaned data or accidental data loss.
**Owner:** Data Engineering.

---

## Why the distinction matters for migration

| Table Type | On-Prem Behavior | Migration Implication |
|---|---|---|
| **External** | `DROP TABLE` removes only metadata; underlying HDFS data is untouched | Safe to iterate on the table definition in the target without risk to the underlying migrated data — re-creating the table definition doesn't touch the data in GCS |
| **Managed** | `DROP TABLE` removes both metadata and underlying data | Requires more care — recreating a "managed" table pattern in the target must not be interpreted as safe to drop/recreate carelessly, since a Hive-pattern managed table on Dataproc-Hive still ties data lifecycle to the table definition |

## Recommended target pattern: prefer external tables

For nearly all migrated tables, the recommended target pattern (whether
BigQuery or Dataproc-Hive) is **external-table-equivalent**: the
underlying data in GCS is the authoritative, independently-managed asset
(per
[`04-target-architecture/04-storage-architecture.md`](../04-target-architecture/04-storage-architecture.md)
zoning), and the table/view definition is a separate, freely-recreatable
layer on top.

- **BigQuery:** use native tables loaded from GCS (not BigQuery external
  tables reading GCS directly, unless the specific hybrid case from
  [`04-target-architecture/05-data-warehouse-architecture.md`](../04-target-architecture/05-data-warehouse-architecture.md)
  applies) — but treat the GCS curated zone as the durable source of
  truth, with BigQuery load jobs as a re-runnable, non-destructive
  population step.
- **Dataproc-Hive:** use genuine external tables (`CREATE EXTERNAL TABLE
  ... LOCATION 'gs://...'`), matching the on-prem external table pattern
  directly.

This significantly reduces migration risk: if a table definition needs to
be fixed or recreated, doing so never risks the underlying data.

## Handling on-prem managed tables

For any on-prem table confirmed as Hive-managed (not external) in
[`01-discovery/inventories/09-hive-inventory.md`](../01-discovery/inventories/09-hive-inventory.md):

1. Confirm this is intentional (managed tables are less common in
   well-architected Hadoop estates but do occur, often for smaller,
   frequently-rewritten tables).
2. Migrate the underlying data per
   [`05-storage-migration/`](../05-storage-migration/README.md) and
   [`06-data-migration/`](../06-data-migration/README.md) as with any
   other table.
3. Recreate as an external-table-equivalent pattern in the target
   (per the recommendation above) **unless** there's a specific,
   documented reason the managed-table lifecycle coupling is actually
   desired — record that reasoning explicitly if so, since it's a
   deliberate deviation from the default pattern.

## Migration checklist per table

| Step | External Table | Managed Table |
|---|---|---|
| Data migration | Standard, per [`06-data-migration/`](../06-data-migration/README.md) | Standard, same procedure |
| Table definition creation in target | `CREATE EXTERNAL TABLE` / native BigQuery table load, pointing at already-migrated GCS data | Same — target pattern recreates as external-equivalent regardless of source table type |
| Risk of accidental data loss from a definition change | Low | N/A after migration — target pattern removes this risk going forward |

## Common Mistakes

- Assuming all on-prem tables are external without checking — a managed
  table migrated as if external (i.e., someone later runs a careless
  `DROP TABLE` on the on-prem source assuming it's safe) can cause
  accidental data loss on the source before the migration for that table
  is even complete.
- Recreating a genuinely managed-table lifecycle unnecessarily in the
  target — this reintroduces the "DROP TABLE deletes my data" risk that
  the external-table-equivalent target pattern is specifically designed to
  eliminate.

## Production Notes

Explicitly confirm table type (external vs. managed) for every Tier 1
table before any DDL work begins — this is a five-minute check
(`DESCRIBE FORMATTED <table>` shows "Table Type") that prevents a
potentially catastrophic mistake.
