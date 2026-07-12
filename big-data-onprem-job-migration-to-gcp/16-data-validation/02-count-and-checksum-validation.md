# Count & Checksum Validation

**Purpose:** The generalized, reusable form of the count/checksum checks
already introduced in
[`05-storage-migration/05-checksum-and-validation.md`](../05-storage-migration/05-checksum-and-validation.md)
(file-level) and
[`06-data-migration/07-data-reconciliation-framework.md`](../06-data-migration/07-data-reconciliation-framework.md)
(migration-time, row-level) — implemented as a standard, config-driven
check type in the validation engine.
**Owner:** Data Engineering.

---

## Check types

| Check | Implementation |
|---|---|
| Row count | `SELECT COUNT(*)` on both source and target, compared with the configured tolerance (default: 0 for exact match) |
| Column-level checksum (row-level content verification) | Hash each row's concatenated column values (e.g., `MD5(CONCAT(col1, col2, ...))`), compare the set of hashes between source and target — catches content differences that row count alone would miss |
| Table-level checksum | Aggregate hash of all row-level checksums (e.g., `SUM(CAST(CONV(SUBSTR(MD5(...), 1, 15), 16, 10) AS FLOAT64))` or an equivalent order-independent aggregate hash), providing one number to compare per table |

## When to use row-level vs. table-level checksums

| Situation | Approach |
|---|---|
| Investigating a known or suspected discrepancy | Row-level checksums, to pinpoint exactly which rows differ |
| Routine, frequent (e.g., daily) automated validation across many tables | Table-level checksum — cheaper to compute and compare at scale, sufficient to detect *that* a discrepancy exists, triggering row-level investigation only when needed |

## Example implementation (BigQuery)

```sql
-- Table-level checksum, order-independent
SELECT
  MOD(SUM(CAST(CONCAT('0x', SUBSTR(TO_HEX(MD5(TO_JSON_STRING(t))), 1, 15)) AS INT64)), 9223372036854775807) AS table_checksum
FROM `project.dataset.table` AS t;
```

Applied identically (accounting for source-platform SQL dialect
differences) against the on-prem Hive source during parallel-run, and the
BigQuery/Dataproc-Hive target — a matching checksum is strong evidence of
row-for-row content equivalence without needing to compare every column
value explicitly.

## Handling expected, legitimate differences

Some differences are expected and not real discrepancies:

- **Floating-point representation** — configure a small numeric tolerance
  for aggregate comparisons rather than exact checksum matching for
  float-typed columns specifically.
- **Timestamp precision differences** between platforms — normalize
  precision before hashing/comparing if the source and target systems
  store timestamps at different granularity.

Document every accepted tolerance explicitly in the table's validation
config, with the reasoning — never silently loosen a check without
recording why.

## Common Mistakes

- Using row-level checksums for routine daily validation across hundreds
  of tables, incurring unnecessary compute cost when a cheaper table-level
  checksum would suffice for routine monitoring.
- Applying exact-match tolerance to floating-point aggregate comparisons,
  producing false-positive failures from harmless representation
  differences that erode trust in the validation framework over time.

## Production Notes

For Tier 1 tables, run row-level checksum validation (not just table-level)
at least once during the parallel-run period, even though table-level is
sufficient for ongoing routine checks — this establishes a higher-
confidence baseline before relying on the cheaper table-level check for
continuous production monitoring.
