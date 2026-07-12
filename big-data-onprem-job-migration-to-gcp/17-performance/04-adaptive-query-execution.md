# Adaptive Query Execution (AQE)

**Purpose:** AQE, enabled by default in the shared
`SparkSessionFactory` (per
[`07-spark-migration/examples/spark_session_factory.py`](../07-spark-migration/examples/spark_session_factory.py)),
dynamically re-optimizes query plans at runtime based on actual observed
data statistics — this document explains what it does and how to verify
it's helping, not just assume it is.
**Owner:** Platform Engineering.

---

## What AQE does

| AQE Feature | What It Solves |
|---|---|
| Dynamically coalescing shuffle partitions | Removes the need to hand-tune `spark.sql.shuffle.partitions` for every job's specific data volume — AQE merges small post-shuffle partitions automatically |
| Dynamically switching join strategies | Converts a planned shuffle join to a broadcast join at runtime if the actual (not estimated) size of one side turns out to be small enough |
| Dynamically optimizing skewed joins | Splits oversized partitions caused by data skew into smaller sub-partitions automatically — see [`06-skew-handling.md`](06-skew-handling.md) for when this alone isn't sufficient |

## Configuration

```
spark.sql.adaptive.enabled = true
spark.sql.adaptive.coalescePartitions.enabled = true
spark.sql.adaptive.skewJoin.enabled = true
```

All enabled by default via the shared `SparkSessionFactory` — no job
should need to configure these individually, consistent with the
don't-repeat-yourself principle in
[`07-spark-migration/08-oop-design-patterns.md`](../07-spark-migration/08-oop-design-patterns.md).

## Verifying AQE is actually helping

Compare the Spark UI's **planned** query plan (shown before execution)
against the **actual/adaptive** plan (shown after, reflecting AQE's
runtime adjustments) — a job where these differ meaningfully (partition
count changed, join strategy changed) is a job genuinely benefiting from
AQE; a job where they're identical suggests AQE isn't finding much to
adjust for that specific workload, which is fine but useful to know when
prioritizing further tuning effort elsewhere.

## When AQE isn't enough

AQE is a strong default but doesn't eliminate the need for the other
tuning techniques in this folder — it reduces, but doesn't remove, the
value of explicit broadcast hints for well-understood small tables (per
[`03-broadcast-joins.md`](03-broadcast-joins.md)), and severe skew may
still require the explicit techniques in
[`06-skew-handling.md`](06-skew-handling.md) beyond AQE's automatic skew
join handling.

## Common Mistakes

- Assuming AQE alone is sufficient and skipping deliberate tuning
  entirely — AQE is a safety net and optimizer, not a substitute for
  understanding a job's actual data characteristics.
- Not verifying AQE is actually enabled for a specific job run (e.g., if
  a job explicitly overrides Spark config in a way that disables it) —
  confirm via the Spark UI's environment tab, not just by checking the
  shared factory's defaults.

## Production Notes

Since the shared `SparkSessionFactory` was on Spark 2.4.8 origin systems
(pre-AQE, introduced in Spark 3.0) per
[`03-current-environment/03-spark-environment-assessment.md`](../03-current-environment/03-spark-environment-assessment.md),
this is a genuine new capability the migration unlocks — flag this
explicitly as a "quick win" performance improvement when communicating
migration benefits to stakeholders in
[`00-project-overview/01-executive-summary.md`](../00-project-overview/01-executive-summary.md)-style
materials.
