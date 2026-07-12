# Broadcast Joins

**Purpose:** Identify and apply broadcast joins where a large shuffle join
can be avoided entirely — one of the highest-leverage, lowest-risk
performance optimizations available, directly applicable to the pricing
zone-lookup pattern used throughout this repository's examples.
**Owner:** Platform Engineering.

---

## When a broadcast join applies

A broadcast join replaces an expensive shuffle join with a much cheaper
pattern when one side of the join is small enough to fit in every
executor's memory — the small table is sent ("broadcast") to every
executor, and the join happens locally without a shuffle of the large
table.

| Join Pattern in This Platform | Broadcast Candidate? |
|---|---|
| `pricing.daily_price_snapshot` joined to a small `zone_lookup` table (per the example job in [`07-spark-migration/examples/example_pricing_job.py`](../07-spark-migration/examples/example_pricing_job.py)) | Yes — zone lookup tables are typically small (hundreds to low thousands of rows) |
| `fraud.txn_feature_scores` joined to a large historical transaction table | No — both sides are large; shuffle join is appropriate, focus tuning there on shuffle/skew instead |
| Any join against a reference/dimension table (product catalog subset, region mapping) | Usually yes, if the reference table is genuinely small |

## Explicit broadcast hint

Don't rely solely on Spark's automatic broadcast threshold detection for
Tier 1 jobs — apply an explicit hint for clarity and to guarantee the
optimization is applied even if automatic detection's size estimate is
off:

```python
from pyspark.sql.functions import broadcast

result = pricing_df.join(broadcast(zone_lookup_df), on="region", how="left")
```

## Automatic broadcast threshold

```
spark.sql.autoBroadcastJoinThreshold = 10485760  # 10MB default; tune upward
                                                    # for confirmed-small tables
                                                    # larger than the default
```

Combined with AQE (per
[`04-adaptive-query-execution.md`](04-adaptive-query-execution.md)),
Spark 3.x can also dynamically convert a shuffle join to a broadcast join
at runtime if the actual (not estimated) size of one side turns out to be
small — but explicit hints remain valuable for the highest-confidence,
most-frequently-run joins for readability and guaranteed behavior.

## Common Mistakes

- Broadcasting a table that's actually too large, causing executor memory
  pressure and potential OOM errors — verify actual table size, don't
  assume "it's a lookup table so it must be small."
- Missing broadcast opportunities because the join was written without
  considering table size characteristics at all — review every join in a
  Tier 1 job's transformation logic specifically for broadcast
  applicability during performance tuning.

## Production Notes

For the pricing zone-mapping join specifically (a recurring pattern across
several job families per
[`01-discovery/inventories/09-hive-inventory.md`](../01-discovery/inventories/09-hive-inventory.md)),
document the broadcast pattern once in the shared library's transformation
utilities (per
[`07-spark-migration/08-oop-design-patterns.md`](../07-spark-migration/08-oop-design-patterns.md))
so every job using a similar lookup-join pattern benefits automatically,
rather than re-discovering this optimization independently per job.
