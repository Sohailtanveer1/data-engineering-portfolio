# 08 — Hive Migration

## Purpose

Migrate the Hive Metastore's logical structure — databases, tables, views,
partitions, statistics, and UDFs — to the per-table BigQuery/Dataproc-Hive
targets decided in
[`04-target-architecture/05-data-warehouse-architecture.md`](../04-target-architecture/05-data-warehouse-architecture.md).
This phase is the logical/schema layer that sits on top of the physical
data already moved by
[`05-storage-migration/`](../05-storage-migration/README.md) and
[`06-data-migration/`](../06-data-migration/README.md).

## Owner

**Data Engineering**, coordinated by Platform Engineering for the
Metastore infrastructure component.

## Inputs

- Hive inventory with per-table target decisions from
  [`01-discovery/inventories/09-hive-inventory.md`](../01-discovery/inventories/09-hive-inventory.md)
  and
  [`04-target-architecture/05-data-warehouse-architecture.md`](../04-target-architecture/05-data-warehouse-architecture.md).
- UDF inventory from
  [`01-discovery/inventories/09-hive-inventory.md`](../01-discovery/inventories/09-hive-inventory.md).
- Migrated table data from
  [`06-data-migration/`](../06-data-migration/README.md).

## Outputs

- Every in-scope table's schema recreated correctly in its GCP target.
- Every view's logic recreated and validated.
- Every UDF reimplemented and validated for behavioral equivalence.
- A Dataproc Metastore instance (for the subset of tables targeting
  Dataproc-Hive) provisioned and populated.

## Prerequisites

[`06-data-migration/`](../06-data-migration/README.md) in progress or
complete for the relevant tables; per-table target decisions finalized.

## Deliverables

1. Hive Metastore migration strategy (for tables targeting Dataproc-Hive).
2. External vs. managed table migration handling.
3. Partition migration procedure.
4. Statistics migration/recomputation approach.
5. View migration procedure.
6. UDF migration procedure.
7. End-to-end execution runbook.

## Risks

- **UDF behavioral drift** — a reimplemented UDF that looks equivalent but
  handles an edge case differently (e.g., null handling, locale-specific
  string formatting) silently changes every query result depending on it.
- **View chains breaking** — a multi-layer view chain (view built on view)
  migrated out of dependency order produces broken intermediate views.
- **Missing/stale statistics** degrading query performance on the new
  platform even though the data itself migrated correctly.

## Rollback

Schema/view/UDF migration for a table is safely re-runnable — DDL can be
dropped and recreated in the target without affecting the on-prem source,
consistent with the non-destructive migration principle established in
[`05-storage-migration/07-rollback-procedure.md`](../05-storage-migration/07-rollback-procedure.md).

## Validation

Every migrated table's schema, every view's output, and every UDF's
behavior must be validated against representative on-prem query output
before being marked complete — see
[`07-execution-runbook.md`](07-execution-runbook.md).

## Best Practices

Migrate UDFs and their dependent views/queries together as one unit, in
dependency order (base tables → views built directly on them → views built
on those views), never in isolation.

## Lessons Learned

UDF reimplementation is consistently underestimated — a UDF that looks
like a simple string transformation often has accumulated undocumented
edge-case handling over years of production use that isn't visible from
reading the current implementation alone; the safest validation is
side-by-side output comparison, not code review.

## Common Mistakes

- Migrating a view's logic by hand-translating its `SHOW CREATE VIEW`
  output without verifying the syntax translates identically between Hive
  SQL and BigQuery Standard SQL (or the Dataproc-Hive equivalent) — subtle
  SQL dialect differences (date functions, implicit type casting) are a
  common silent-bug source.
- Treating table statistics as unimportant "since the data is the same" —
  stale or missing statistics measurably degrade BigQuery/Spark query
  planning and performance.

## Production Notes

For any UDF used in `pricing`, `fraud`, or `finance` queries, require
explicit sign-off from the query's business owner on a side-by-side output
comparison before considering that UDF's migration complete.

---

## Folder structure

```
08-hive-migration/
├── README.md                                      This file
├── 01-metastore-migration-strategy.md              Dataproc Metastore provisioning and population
├── 02-external-vs-managed-table-migration.md       Handling each table type correctly
├── 03-partition-migration.md                       Partition metadata migration procedure
├── 04-statistics-migration.md                       Statistics recomputation approach
├── 05-view-migration.md                             View migration in dependency order
├── 06-udf-migration.md                              UDF reimplementation and validation
└── 07-execution-runbook.md                          End-to-end per-table/view/UDF runbook
```
