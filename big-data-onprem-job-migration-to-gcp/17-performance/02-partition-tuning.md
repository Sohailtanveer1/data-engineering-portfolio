# Partition Tuning (Spark Runtime)

**Purpose:** Distinct from the storage-layer partition **strategy** in
[`06-data-migration/05-partition-strategy.md`](../06-data-migration/05-partition-strategy.md)
(how data is laid out in GCS/BigQuery), this document covers Spark
**runtime** partitioning — how a job splits its in-memory/in-flight
processing work, which directly determines parallelism and resource
utilization.
**Owner:** Platform Engineering.

---

## Reading partitioned source data efficiently

When reading from the partitioned GCS/BigQuery layout established in
[`06-data-migration/05-partition-strategy.md`](../06-data-migration/05-partition-strategy.md),
ensure **partition pruning** is actually effective:

```python
# GOOD — filter pushed down, only relevant partitions read
df = spark.read.parquet("gs://acme-prod-pricing-curated/daily_price_snapshot/") \
    .filter(F.col("dt") == run_date)

# BAD — reads all partitions then filters in-memory, defeating pruning
df = spark.read.parquet("gs://acme-prod-pricing-curated/daily_price_snapshot/")
all_data = df.collect()
filtered = [row for row in all_data if row["dt"] == run_date]
```

Confirm pruning is actually occurring by inspecting the Spark UI's
"Input Size" metric for the read stage — it should reflect only the
filtered partition's size, not the full table.

## Sizing runtime partition count

| Situation | Guidance |
|---|---|
| Reading a large, evenly-distributed dataset | Default partition count from the source file layout (Parquet row groups) is usually reasonable; verify partition count isn't excessively high (many tiny partitions) or low (few oversized partitions) via `df.rdd.getNumPartitions()` |
| Post-shuffle stages (joins, aggregations) | Governed by `spark.sql.shuffle.partitions` or AQE's dynamic coalescing, per [`01-shuffle-tuning.md`](01-shuffle-tuning.md) |
| Writing output | Explicitly repartition/coalesce before write to avoid the small-files problem — see below |

## Avoiding the small-files problem on write

```python
# Coalesce to a reasonable file count before writing, avoiding thousands
# of tiny output files that degrade downstream read performance and
# increase GCS request overhead/cost.
(
    df
    .coalesce(estimate_optimal_file_count(df))  # sized to target ~128-256MB per output file
    .write.mode("overwrite")
    .partitionBy("dt")
    .parquet(output_path)
)
```

Too many small output files is a common, easy-to-miss performance and
cost issue — every small file adds GCS request overhead to every
downstream read, compounding across every job that later reads this
output.

## Common Mistakes

- Using `repartition()` (a full shuffle) when `coalesce()` (no shuffle,
  reduces partition count only) would suffice for reducing output file
  count — `coalesce()` is significantly cheaper when only reducing, not
  increasing, partition count.
- Not verifying partition pruning is actually working, silently paying
  the cost of reading far more data than necessary on every run.

## Production Notes

For every Tier 1 job, verify partition pruning behavior explicitly by
comparing "Input Size" in the Spark UI against the expected size of just
the relevant partition — do this once during
[`15-testing/`](../15-testing/README.md) and re-verify if the read
pattern changes materially in a future code update.
