# 06 — Data Migration

## Purpose

[`05-storage-migration/`](../05-storage-migration/README.md) moves raw
bytes from HDFS to GCS. This phase is the **logical/table-level** data
migration layer on top of that: how historical data is backfilled, how
ongoing incremental loads work once a job has cut over, whether CDC is
needed anywhere, how partitioning and file format are standardized, and
how migrated data is reconciled against its source at the table/dataset
level — distinct from the file-integrity checksum validation already
covered in
[`05-storage-migration/05-checksum-and-validation.md`](../05-storage-migration/05-checksum-and-validation.md).

## Owner

**Data Engineering**, coordinated by the Migration Program Lead.

## Inputs

- Completed or in-progress storage migration for the relevant domain
  ([`05-storage-migration/`](../05-storage-migration/README.md)).
- Hive inventory and per-table target decisions from
  [`01-discovery/inventories/09-hive-inventory.md`](../01-discovery/inventories/09-hive-inventory.md)
  and
  [`04-target-architecture/05-data-warehouse-architecture.md`](../04-target-architecture/05-data-warehouse-architecture.md).
- External database/Sqoop dependency detail from
  [`02-dependency-analysis/methodology/07-database-and-rest-api-dependencies.md`](../02-dependency-analysis/methodology/07-database-and-rest-api-dependencies.md).

## Outputs

- Every in-scope table's historical data fully backfilled and reconciled
  in its GCP target (BigQuery or Dataproc-Hive).
- A working incremental load mechanism for every table that previously
  relied on Sqoop incremental import or streaming ingestion.
- A standardized partitioning and file-format approach applied
  consistently, replacing legacy inconsistent conventions.

## Prerequisites

[`04-target-architecture/`](../04-target-architecture/README.md) gated
(per-table BigQuery/Dataproc-Hive decisions finalized);
[`05-storage-migration/`](../05-storage-migration/README.md) in progress
or complete for the relevant data domain.

## Deliverables

1. Historical data migration plan (backfill batching strategy).
2. Incremental load strategy (watermark-based, replacing Sqoop
   incremental import patterns).
3. CDC strategy for the subset of sources that require it.
4. Snapshot strategy for point-in-time reconciliation and rollback
   support.
5. Partition strategy standard.
6. Format and compression strategy standard.
7. Data reconciliation framework (migration-time, table-level).
8. End-to-end per-table migration execution runbook.

## Risks

- **Historical backfill volume exceeding practical batch windows** for
  very large tables — mitigated by the batching strategy in
  [`01-historical-data-migration-plan.md`](01-historical-data-migration-plan.md).
- **Incremental load watermark logic ported incorrectly**, causing
  duplicate or missed records — the single most common data-migration bug
  category, mitigated by the explicit watermark redesign in
  [`02-incremental-load-strategy.md`](02-incremental-load-strategy.md)
  rather than a mechanical port of the Sqoop watermark mechanism.
- **Reconciliation performed only at the storage-byte level**
  ([`05-storage-migration/`](../05-storage-migration/README.md)) without
  the additional logical/business reconciliation this phase requires —
  the two are complementary, not substitutes for each other.

## Rollback

Historical loads are re-runnable (idempotent by design, see
[`01-historical-data-migration-plan.md`](01-historical-data-migration-plan.md));
incremental loads can be paused and the job's read path reverted to
on-prem per
[`05-storage-migration/07-rollback-procedure.md`](../05-storage-migration/07-rollback-procedure.md)
job-level rollback guidance.

## Validation

Every table's migrated data must pass the reconciliation framework in
[`07-data-reconciliation-framework.md`](07-data-reconciliation-framework.md)
before being marked complete in
[`14-job-migration/`](../14-job-migration/README.md). This is
migration-time validation; ongoing production validation is the scope of
[`16-data-validation/`](../16-data-validation/README.md).

## Best Practices

Design every load (historical and incremental) to be idempotent and safely
re-runnable — this is both a data-safety requirement and a practical
necessity, since migration loads routinely need retries.

## Lessons Learned

The most common source of post-cutover data discrepancy is not the bulk
storage transfer (which is well-validated by
[`05-storage-migration/`](../05-storage-migration/README.md)) but a subtly
incorrect incremental-load watermark carried forward from the Sqoop-era
logic without being re-examined for correctness in the new pattern.

## Common Mistakes

- Treating historical backfill as a single monolithic job instead of
  batching it — a single multi-terabyte backfill job that fails 90% of the
  way through wastes far more time than a batched, resumable approach.
- Copying Sqoop's incremental-import watermark column/logic verbatim
  without confirming it still means the same thing in the new pipeline
  (e.g., a "last modified" column that wasn't reliably maintained by the
  source system).

## Production Notes

For Tier 1 tables, historical backfill should be executed and reconciled
well ahead of that table's job cutover date — leaving backfill for the
final days before cutover removes any buffer for handling an unexpected
volume or reconciliation issue.

---

## Folder structure

```
06-data-migration/
├── README.md                                   This file
├── 01-historical-data-migration-plan.md         Backfill batching strategy
├── 02-incremental-load-strategy.md              Watermark-based ongoing loads
├── 03-cdc-strategy.md                           Change data capture, where required
├── 04-snapshot-strategy.md                      Point-in-time snapshots
├── 05-partition-strategy.md                     Standardized partitioning scheme
├── 06-format-and-compression-strategy.md        Parquet/Avro/ORC and compression standard
├── 07-data-reconciliation-framework.md          Migration-time, table-level reconciliation
└── 08-migration-execution-runbook.md            End-to-end per-table runbook
```
