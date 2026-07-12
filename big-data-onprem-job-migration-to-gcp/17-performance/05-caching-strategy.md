# Caching Strategy

**Purpose:** Use Spark's `.cache()`/`.persist()` deliberately, where a
DataFrame is reused multiple times within a job — a frequently
misapplied optimization that can hurt as much as help if used carelessly.
**Owner:** Platform Engineering.

---

## When caching helps

Caching is valuable when a DataFrame is computed once (an expensive read
or transformation) and then **reused multiple times** in the same job —
without caching, Spark recomputes the full lineage from scratch on every
reuse.

```python
zone_lookup_df = spark.read.parquet(zone_lookup_path).cache()

# Reused across multiple downstream steps — caching avoids re-reading/
# re-computing zone_lookup_df each time.
pricing_with_zones = apply_zone_mapping(pricing_df, zone_lookup_df)
inventory_with_zones = apply_zone_mapping(inventory_df, zone_lookup_df)
```

## When caching hurts

- **Caching a DataFrame used only once** — pure overhead (memory pressure,
  serialization cost) with no benefit.
- **Caching a very large DataFrame** without sufficient executor memory —
  causes spill to disk, which can be slower than simply recomputing.
- **Forgetting to `.unpersist()`** a cached DataFrame once it's no longer
  needed within a long-running job, holding memory unnecessarily for the
  remainder of execution.

## Storage level selection

| Storage Level | When to Use |
|---|---|
| `MEMORY_ONLY` (default for `.cache()`) | Small-to-medium DataFrames that comfortably fit in available executor memory |
| `MEMORY_AND_DISK` | Larger DataFrames where memory pressure is a risk — spills to disk gracefully rather than losing the cached data and forcing full recomputation |
| Explicit `.unpersist()` | Always call once a cached DataFrame is no longer needed, don't rely on Spark's LRU eviction alone for predictable memory management |

## Verifying caching is helping

Use the Spark UI's "Storage" tab to confirm a DataFrame is actually
cached as expected (not partially cached due to insufficient memory,
which silently degrades to recomputation for the uncached portions) and
compare stage execution times with and without caching during performance
testing to confirm a real, measurable benefit before keeping the caching
call in production code.

## Common Mistakes

- Caching every DataFrame "just in case," without confirming reuse
  actually occurs — this is a very common over-application that hurts
  performance rather than helping.
- Never calling `.unpersist()`, causing memory pressure to accumulate over
  a job with many transformation steps.

## Production Notes

For the zone-lookup pattern (reused across the pricing job family's
transformations), caching is a confirmed, validated optimization — but
don't generalize this to assume caching is universally beneficial for
every job; validate per job during
[`15-testing/08-performance-testing-overview.md`](../15-testing/08-performance-testing-overview.md).
