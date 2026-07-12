# Skew Handling

**Purpose:** Address data skew (a small number of keys with disproportionately
large volume) — a common, high-impact performance problem in ecommerce
data specifically (a handful of best-selling SKUs, a small number of very
active customer accounts, a few high-volume vendor feeds) that AQE's
automatic skew handling doesn't always fully resolve on its own.
**Owner:** Platform Engineering.

---

## Recognizing skew

In the Spark UI, skew shows up as a small number of tasks within a stage
taking dramatically longer than the rest — while most tasks complete
quickly, the job's overall duration is dominated by the few slow,
skewed tasks.

## Ecommerce-specific skew examples

| Scenario | Skew Source |
|---|---|
| Joining transaction data by `sku` | A handful of best-selling products have vastly more transaction rows than the long tail |
| Aggregating by `customer_id` | A small number of high-activity accounts (e.g., B2B bulk purchasers) dominate |
| Joining by `vendor_id` in a vendor feed reconciliation job | A few large vendors contribute disproportionate volume vs. many small vendors |
| Fraud scoring aggregated by `merchant_category` | Certain categories naturally see far higher transaction volume |

## Techniques beyond AQE's automatic skew join handling

### Salting

For severe skew not fully resolved by AQE, add a synthetic "salt" key to
spread a hot key's rows across multiple partitions:

```python
from pyspark.sql import functions as F

SALT_BUCKETS = 20

salted_txns = transactions_df.withColumn(
    "salt", (F.rand() * SALT_BUCKETS).cast("int")
)
salted_skus = sku_dim_df.crossJoin(
    spark.range(SALT_BUCKETS).withColumnRenamed("id", "salt")
)

result = salted_txns.join(
    salted_skus,
    on=["sku", "salt"],
    how="inner",
).drop("salt")
```

Salting adds complexity — reserve it for confirmed severe skew where AQE's
automatic handling and broadcast join conversion (per
[`03-broadcast-joins.md`](03-broadcast-joins.md)) aren't sufficient,
validated via actual measured stage duration improvement, not applied
speculatively.

### Isolating and handling hot keys separately

For a small, known set of extreme outlier keys (e.g., the top 5 best-
selling SKUs), consider explicitly splitting the job's processing: handle
the hot keys with dedicated, appropriately-sized processing, and the long
tail with standard processing — more implementation complexity, but can
be simpler to reason about than a generic salting approach for a
genuinely small number of outliers.

## Common Mistakes

- Applying salting broadly as a default technique instead of confirming
  skew is actually present and AQE's automatic handling is genuinely
  insufficient first — salting adds real complexity and shouldn't be a
  default optimization.
- Not testing skew handling against real production key distributions —
  a uniformly-distributed synthetic test dataset won't reveal a skew
  problem that only manifests with real, naturally skewed ecommerce data.

## Production Notes

For any Tier 1 job joining or aggregating by `sku`, `customer_id`, or
`vendor_id`, explicitly test with a **real, production-representative key
distribution** (not synthetic uniform test data) during
[`15-testing/08-performance-testing-overview.md`](../15-testing/08-performance-testing-overview.md)
— skew is exactly the kind of issue that looks fine in a naive test and
only surfaces under real data characteristics.
