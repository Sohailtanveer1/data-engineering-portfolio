# Spark Version & Deprecated API Migration

**Purpose:** Define the target Spark version and the systematic process
for identifying and remediating deprecated/removed API usage, scoped using
the version distribution data from
[`01-discovery/inventories/08-spark-inventory.md`](../01-discovery/inventories/08-spark-inventory.md)
and
[`03-current-environment/03-spark-environment-assessment.md`](../03-current-environment/03-spark-environment-assessment.md).
**Owner:** Platform Engineering.

---

## Target version

The target Spark version is the latest version supported by the current
Dataproc image family at the time [`12-cluster-design/`](../12-cluster-design/README.md)
is finalized (Dataproc image release notes are the authoritative source —
confirm at execution time, not from this document, since Dataproc-supported
versions change over time). This document assumes a Spark 2.x → Spark 3.x
upgrade, the most common scenario for an estate identified as running
Spark 2.4.x in Discovery.

## Deprecated / removed API categories to check for

| Category | Spark 2.x Pattern | Spark 3.x Replacement |
|---|---|---|
| SQL context | `SQLContext`, `HiveContext` | `SparkSession` (unified entry point) |
| DataFrame/Dataset creation from RDD | `sqlContext.createDataFrame(rdd, schema)` patterns tied to `SQLContext` | `spark.createDataFrame(rdd, schema)` via `SparkSession` |
| Implicit schema inference behavior changes | Certain type inference defaults changed between major versions (e.g., CSV/JSON inference edge cases) | Explicit schema definition required per the coding standard — removes ambiguity entirely rather than relying on version-specific inference behavior |
| Deprecated ML library APIs (`spark.mllib` RDD-based API) | `org.apache.spark.mllib.*` | `org.apache.spark.ml.*` (DataFrame-based) |
| Legacy date/timestamp parsing behavior | Spark 2.x's more lenient legacy parser | Spark 3.x's default ISO-based parser — requires explicit review of any custom date format strings, since parsing behavior for ambiguous formats changed |
| `spark.sql.shuffle.partitions` defaults and AQE interaction | Static shuffle partition count, no AQE | Adaptive Query Execution (AQE) available and recommended — see [`17-performance/`](../17-performance/README.md) |

## Identification process

1. **Static scan** every job's source code for the deprecated API patterns
   above (extend the grep/static-analysis tooling already built for
   [`02-dependency-analysis/methodology/01-spark-job-dependencies.md`](../02-dependency-analysis/methodology/01-spark-job-dependencies.md)).
2. **Compile/build against the target Spark version** in a non-production
   branch for every job — compilation errors and deprecation warnings
   (Scala/Java) or `DeprecationWarning`s (PySpark) surface the majority of
   required changes mechanically.
3. **Behavioral review** for the categories above that don't cause a
   compile error but silently change behavior (date parsing, schema
   inference) — these require a manual review pass, not just a build-pass
   check, since incorrect output without an error is the higher-risk
   failure mode.
4. **Run existing tests (if any) against the target version** to catch
   behavioral regressions the static/compile checks miss.

## Per-job remediation tracking

| Job ID | Current Spark Version | Deprecated APIs Found | Remediation Status | Behavioral Review Needed? |
|---|---|---|---|---|
| EX-001 | 2.4.8 | `SQLContext`, legacy date parsing in zone lookup | In progress | Yes — date parsing change reviewed with job owner |
| EX-003 | 2.4.8 | None found | Complete | No |

_(Populate exhaustively per job from
[`01-discovery/inventories/08-spark-inventory.md`](../01-discovery/inventories/08-spark-inventory.md).)_

## Handling jobs on very old (pre-2.x) Spark versions

If Discovery surfaced any job on a materially older version (e.g., Spark
1.6.x, per assumption A4 in
[`00-project-overview/06-assumptions-and-constraints.md`](../00-project-overview/06-assumptions-and-constraints.md)),
treat this as a **separate, explicitly scoped major-version-jump effort**,
not a standard migration — the effort estimate and risk profile are
materially different, and this should be flagged to the Migration Program
Lead for separate timeline/resourcing consideration rather than folded
into standard wave planning.

## Common Mistakes

- Relying solely on "it compiled" as proof of correctness — several
  Spark 2→3 behavioral changes (date parsing, certain implicit type
  coercions) do not cause compile errors but silently change output.
- Deferring behavioral review for date/timestamp handling — this is
  consistently the highest-impact, easiest-to-miss category of Spark 2→3
  migration bugs.

## Production Notes

For any Tier 1 job with date/timestamp-based business logic (nearly all of
them, in an ecommerce context — order dates, pricing effective dates,
fraud scoring windows), explicitly test date parsing/formatting behavior
against the target Spark version with real historical edge-case dates
(month boundaries, year boundaries, DST transitions if timezone-aware)
before considering the migration validated.
