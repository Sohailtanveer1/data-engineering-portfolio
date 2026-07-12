# Duplicate & Null Detection

**Purpose:** Standard, automated checks for two of the most common data
quality issues introduced by migration bugs — non-idempotent writes
(duplicates) and format-conversion mishandling (unexpected nulls).
**Owner:** Data Engineering.

---

## Duplicate detection

```sql
-- Standard duplicate check pattern, parameterized by key_columns per table config
SELECT sku, dt, COUNT(*) AS duplicate_count
FROM `project.dataset.daily_price_snapshot`
GROUP BY sku, dt
HAVING COUNT(*) > 1;
```

A non-empty result is a hard failure — per the idempotency requirement in
[`07-spark-migration/07-idempotency-design.md`](../07-spark-migration/07-idempotency-design.md),
duplicates should never occur in a correctly-migrated table, and any
occurrence indicates either a non-idempotent write bug or a retry that
didn't properly overwrite/merge.

## Null detection

```sql
-- Standard null check pattern, parameterized by columns and expected_null_count per table config
SELECT
  COUNTIF(sku IS NULL) AS sku_nulls,
  COUNTIF(base_price IS NULL) AS base_price_nulls,
  COUNTIF(discount_percent IS NULL) AS discount_percent_nulls
FROM `project.dataset.daily_price_snapshot`;
```

Compared against the `expected_null_count` in the table's validation
config — some columns may legitimately have an expected non-zero null
rate (e.g., an optional field), while key business columns should have
zero.

## Comparing null rates against the source

Beyond checking for an absolute expected count, compare the **null rate**
between source and target — a significant increase in null rate on the
target for a column that had a low null rate on-prem is a strong signal of
a format-conversion or transformation bug (per the type-inference
ambiguity risk flagged in
[`06-data-migration/06-format-and-compression-strategy.md`](../06-data-migration/06-format-and-compression-strategy.md)).

## Common Mistakes

- Checking duplicate detection only on the full row, missing duplicates on
  the actual business key (e.g., two rows with the same `sku`/`dt` but a
  trivially different value in an unrelated column would still be a
  business-logic duplicate, even if not byte-identical).
- Setting `expected_null_count` once at migration time and never
  revisiting it as legitimate business changes occur (e.g., a new optional
  field is added upstream, legitimately increasing null rate) — review
  expected null counts periodically, not just at initial setup.

## Production Notes

For Tier 1 tables, duplicate detection should run **after every single
job run**, not just periodically — a duplicate introduced by a single bad
run should be caught immediately, not discovered days later during a
routine periodic check.
