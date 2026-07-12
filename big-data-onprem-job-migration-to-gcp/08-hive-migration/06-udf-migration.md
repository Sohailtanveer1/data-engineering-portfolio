# UDF Migration

**Purpose:** Reimplement every custom Hive UDF identified in
[`01-discovery/inventories/09-hive-inventory.md`](../01-discovery/inventories/09-hive-inventory.md)
for the target platform, with rigorous behavioral validation — UDFs are
the highest-risk category of silent logic drift in the entire Hive
migration, since their internal logic is opaque to anyone just reading
query SQL.
**Owner:** Data Engineering, with the original UDF author/maintainer if
still available (per
[`01-discovery/questions/06-developers.md`](../01-discovery/questions/06-developers.md)).

---

## Target implementation per UDF, by destination

| UDF Target Platform | Implementation Approach |
|---|---|
| BigQuery | BigQuery persistent SQL UDF (if logic expressible in SQL) or a BigQuery remote function (if logic requires procedural code — calls out to a Cloud Function/Cloud Run service) |
| Dataproc-Hive (Spark SQL) | Spark SQL UDF (Python `udf()` / Scala `UserDefinedFunction`), registered in the shared library per [`07-spark-migration/08-oop-design-patterns.md`](../07-spark-migration/08-oop-design-patterns.md) conventions |

Prefer a native SQL UDF over a remote function wherever the logic is
expressible in SQL — remote functions add network latency and an
additional deployed service to operate, and should be reserved for logic
genuinely requiring procedural code (e.g., a complex regex library not
available in BigQuery SQL, or a call to an external validation service).

## Migration procedure per UDF

1. **Extract the current implementation.** Locate and read the actual UDF
   source code (Java class for a Hive UDF) — not just its registered name
   and apparent purpose.
2. **Document every observed behavior**, including edge cases: null
   input handling, empty string handling, malformed input handling,
   locale/encoding assumptions. Do not assume — write a test harness
   against the *existing* on-prem UDF with a broad range of inputs and
   record its actual output for each.
3. **Reimplement** in the target language/platform, matching every
   documented behavior from step 2.
4. **Validate via side-by-side comparison**: run the same input set (from
   step 2, plus additional inputs sampled from real production data)
   through both the original and reimplemented UDF, and confirm identical
   output for every case.
5. **Update all migrated views/queries** that reference the UDF to use the
   new implementation, per
   [`05-view-migration.md`](05-view-migration.md) dependency ordering
   (UDFs must be migrated before any view/query depending on them).

## Example: `mask_pii` UDF migration

Referencing the illustrative UDF from
[`01-discovery/inventories/09-hive-inventory.md`](../01-discovery/inventories/09-hive-inventory.md):

| Step | Detail |
|---|---|
| Current behavior documented | Masks all but the last 4 characters of a string; returns `NULL` unchanged for `NULL` input; returns an empty string unchanged for empty string input (confirmed by testing, not assumed) |
| Target implementation | BigQuery SQL UDF: `CREATE FUNCTION pii.mask_pii(input STRING) RETURNS STRING AS (CASE WHEN input IS NULL OR LENGTH(input) = 0 THEN input WHEN LENGTH(input) <= 4 THEN REPEAT('*', LENGTH(input)) ELSE CONCAT(REPEAT('*', LENGTH(input) - 4), SUBSTR(input, -4)) END)` |
| Validation | Side-by-side comparison run against 10,000 sampled real (de-identified for testing purposes, per data handling policy) values from `fraud.txn_feature_scores`, zero discrepancies |

## Common Mistakes

- Reimplementing a UDF from its *name* and assumed purpose rather than its
  actual source code and observed behavior — assumptions about what a UDF
  "probably does" are a common source of subtle reimplementation bugs.
- Skipping edge-case testing (null, empty, malformed input) because the
  "normal" cases match — edge cases are exactly where reimplementations
  diverge, and exactly what's least likely to be caught by a cursory
  review.
- Migrating a UDF used by a Tier 1 query without involving the query's
  business owner in reviewing the validation results.

## Production Notes

For `mask_pii` and any other UDF touching PII, involve Security in
reviewing the reimplementation and its validation results explicitly — a
masking UDF that behaves even slightly differently than intended is a
potential compliance issue, not just a data quality one.
