# Data Reconciliation Framework (Migration-Time)

**Purpose:** Define the table/dataset-level reconciliation checks run at
migration time — after
[`05-storage-migration/05-checksum-and-validation.md`](../05-storage-migration/05-checksum-and-validation.md)
has already confirmed byte-level transfer integrity — to confirm the
*logical* data is correct: right row counts, right aggregates, right
schema, no silent corruption introduced during format conversion or
transformation. The comprehensive, ongoing production validation framework
is [`16-data-validation/`](../16-data-validation/README.md); this document
is scoped specifically to the one-time migration-load validation gate.
**Owner:** Data Engineering.

---

## Reconciliation checks (per table, per migration batch)

| Check | Method | Tolerance |
|---|---|---|
| Row count match | `COUNT(*)` on source snapshot vs. target, at the same logical point in time (per [`04-snapshot-strategy.md`](04-snapshot-strategy.md)) | Exact match required |
| Column-level aggregate match | `SUM()`/`AVG()`/`MIN()`/`MAX()` on key numeric columns (e.g., price, quantity, amount) | Exact match required for financial/pricing columns; documented tolerance for floating-point columns where minor representation differences are expected and explainable |
| Null count match per column | `COUNT(*) WHERE column IS NULL` on source vs. target | Exact match required |
| Distinct value count match on key dimension columns | `COUNT(DISTINCT column)` | Exact match required |
| Schema match | Column names, types, and nullability compared programmatically | Exact match required, or explicitly documented and approved deviation (e.g., a deliberate type widening) |
| Sample row spot-check | Pull N random rows by primary key from both source and target, compare field-by-field | 100% match on sampled rows |
| Duplicate detection | Check for unexpected duplicate primary keys in target that don't exist in source | Zero unexplained duplicates |

## Automated reconciliation script pattern

As with storage-level validation, this should be a reusable, scripted
comparison (see [`scripts/`](../scripts/README.md)), parameterized per
table, producing a pass/fail report with specific discrepancies listed —
not a manual, ad-hoc SQL exercise repeated inconsistently per table.

```
reconcile_table.py \
  --source-conn=hive://<metastore>/<db>.<table> \
  --source-snapshot=migration-recon-<date> \
  --target-conn=bigquery://<project>.<dataset>.<table> \
  --key-columns=<primary-key-columns> \
  --numeric-columns=<columns-for-aggregate-check> \
  --output-report=recon-report-<table>-<date>.json
```

## Handling reconciliation failures

| Failure | Likely Cause | Resolution |
|---|---|---|
| Row count mismatch | Batching gap, snapshot timing mismatch, or a filtering bug in the transformation job | Re-run against a fresh snapshot pair to rule out timing; investigate transformation logic if it persists |
| Aggregate mismatch, matching row count | Type conversion issue (e.g., precision loss in a decimal-to-float conversion) | Review the specific column's type mapping between source and target explicitly |
| Null count mismatch | Format conversion mishandling empty strings vs. actual nulls (a common CSV-to-Parquet conversion pitfall) | Review conversion logic for the affected column type |
| Duplicate keys in target | Non-idempotent load logic (append instead of overwrite/merge) | Fix the load job per the idempotency requirement in [`01-historical-data-migration-plan.md`](01-historical-data-migration-plan.md); re-run the affected batch |

## Sign-off gate

A table's data migration is not marked complete in
[`14-job-migration/`](../14-job-migration/README.md) until:

1. All reconciliation checks above pass, or any deviation is explicitly
   documented and approved (e.g., a deliberate, reviewed type widening).
2. The reconciliation report is reviewed by the table's owning Data
   Engineering team.
3. For Tier 1 tables, the report is also reviewed by the Business Owner's
   designated technical contact, per
   [`01-discovery/inventories/02-business-critical-jobs.md`](../01-discovery/inventories/02-business-critical-jobs.md).

## Common Mistakes

- Running reconciliation once at the end of a full historical backfill
  instead of per-batch — this makes root-causing a discrepancy far harder,
  since the pool of candidate causes spans the entire backfill instead of
  one batch.
- Setting a loose tolerance "to avoid false alarms" on financial/pricing
  columns — for Tier 1 financial data, an exact match is the only
  acceptable tolerance; any mismatch, however small, requires
  investigation, not a defined acceptable variance.

## Production Notes

For fraud and finance tables specifically, retain the full reconciliation
report as part of the audit trail — these reports may be relevant evidence
for a future compliance audit demonstrating the migration was executed
with rigor, not just internally useful for engineering sign-off.
