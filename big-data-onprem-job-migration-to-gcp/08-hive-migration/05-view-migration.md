# View Migration

**Purpose:** Migrate Hive views in the correct dependency order, with SQL
dialect translation where required, validated against the view-chain
analysis already performed in
[`02-dependency-analysis/methodology/02-hive-dependencies.md`](../02-dependency-analysis/methodology/02-hive-dependencies.md).
**Owner:** Data Engineering.

---

## Migration order: base tables → first-layer views → nested views

Using the view dependency chain resolved in
[`02-dependency-analysis/methodology/02-hive-dependencies.md`](../02-dependency-analysis/methodology/02-hive-dependencies.md):

1. Confirm every base table a view depends on is already migrated and
   validated (per [`06-data-migration/`](../06-data-migration/README.md)
   and [`03-partition-migration.md`](03-partition-migration.md)).
2. Migrate views with no dependency on another view first.
3. Migrate views that depend only on already-migrated views next,
   proceeding layer by layer through the full chain.

Attempting to migrate a view before its base dependency exists in the
target produces an immediate, obvious failure (a missing-table error) —
easy to catch — but attempting to migrate views out of order across
*multiple* view layers can produce a working-but-wrong view if an
intermediate view is accidentally pointed at a stale or partial version
of its dependency, which is harder to catch without explicit ordering
discipline.

## SQL dialect translation

| Concern | Hive SQL | BigQuery Standard SQL | Dataproc-Hive (via Spark SQL) |
|---|---|---|---|
| Date functions | `date_add`, `from_unixtime`, Hive-specific format strings | `DATE_ADD`, `FORMAT_TIMESTAMP`, different format string syntax | Largely Spark-SQL-compatible with Hive, lower translation burden |
| String functions | Hive built-ins (`regexp_extract`, etc.) | Mostly compatible, some signature differences | Largely compatible |
| Implicit type coercion | More permissive | Stricter — some implicit casts that work in Hive will error in BigQuery | Spark SQL's coercion rules differ subtly from Hive's in some cases |
| `LATERAL VIEW` / explode patterns | Hive-specific syntax | `UNNEST` | Spark SQL has its own explode syntax, similar to Hive's |

For views targeting BigQuery specifically, expect the most translation
work due to the largest SQL dialect distance; for views targeting
Dataproc-Hive (via Spark SQL), translation is typically minor.

## Migration procedure per view

1. Extract the view's `SHOW CREATE VIEW` definition from the source.
2. Translate the SQL to the target dialect (BigQuery Standard SQL or Spark
   SQL), addressing any of the concerns in the table above found in the
   specific view's logic.
3. Create the view in the target against already-migrated base
   tables/views.
4. **Validate output equivalence**: run the same logical query (or a
   representative sample) against both the on-prem view and the newly
   created target view, compare results row-for-row on a common key.
5. Record the validation result and any deliberate translation decisions
   in [`decisions/`](../decisions/README.md) if the translation required a
   non-obvious choice (e.g., a date function behaving subtly differently).

## Common Mistakes

- Translating SQL syntax mechanically without testing for **behavioral**
  equivalence — syntactically valid, dialect-correct SQL can still produce
  different results due to subtle semantic differences (e.g., NULL
  handling in aggregate functions, different default rounding behavior).
- Migrating a view without first confirming every one of its base table
  dependencies is fully migrated and validated — see
  [`02-dependency-analysis/methodology/02-hive-dependencies.md`](../02-dependency-analysis/methodology/02-hive-dependencies.md)
  for how to resolve the full dependency chain before starting.

## Production Notes

For any view feeding a Tier 1 report or dashboard (per
[`01-discovery/questions/08-data-consumers.md`](../01-discovery/questions/08-data-consumers.md)),
have the actual BI tool/dashboard owner run their real report against the
migrated view in a non-production environment and confirm the output
matches before considering that view's migration complete — an
engineering-only validation can miss discrepancies that only manifest
through the specific way the BI tool queries or aggregates the view.
