"""
pricing_nightly_batch.py — ON-PREM ORIGINAL (Spark 2.4.8, PySpark, HDFS/Hive).

This is the job AS IT ACTUALLY RUNS TODAY on the on-prem cluster, captured
during 07-spark-migration/ dependency review. Preserved here verbatim
(warts included) as the baseline the GCP migration in ../migrated-gcp/ is
validated against — see ../migration-record.md for the full list of
issues found and fixed during migration.

Known issues (do not fix in this file — see migration-record.md):
  - Hardcoded HDFS paths and hostnames throughout
  - No config externalization (spark.yarn.queue, paths, discount cap all inline)
  - SQLContext usage (pre-SparkSession idiom, carried over from Spark 1.x)
  - Non-idempotent write: appends to the output table rather than
    overwriting the target partition, so a re-run duplicates rows
  - No structured logging (print() only)
  - No automated tests
  - Submitted in client mode from an edge node (see run_pricing_nightly.sh)
  - No retry logic — a transient HDFS/network blip fails the whole run
"""

import sys
from pyspark import SparkConf, SparkContext
from pyspark.sql import SQLContext
from pyspark.sql import functions as F

# Hardcoded — no environment separation. Same script runs in "prod" and
# "test" by commenting/uncommenting lines by hand before spark-submit.
HDFS_PRICING_INPUT = "hdfs://nn01.internal.acme.com:8020/data/pricing/daily_price_snapshot/"
HDFS_ZONE_LOOKUP = "hdfs://nn01.internal.acme.com:8020/data/pricing/zone_lookup/"
HDFS_PROMOTIONS = "hdfs://nn01.internal.acme.com:8020/data/pricing/active_promotions/"
HIVE_OUTPUT_TABLE = "pricing.daily_price_snapshot_final"
MAX_DISCOUNT_PERCENT = 40.0  # business rule, buried in code — see 01-discovery/questions/05-business.md


def main():
    if len(sys.argv) < 2:
        print("Usage: pricing_nightly_batch.py <run_date YYYY-MM-DD>")
        sys.exit(1)
    run_date = sys.argv[1]

    conf = SparkConf().setAppName("pricing_nightly_batch")
    sc = SparkContext(conf=conf)
    sqlContext = SQLContext(sc)  # pre-SparkSession idiom

    print("Reading pricing snapshot for %s" % run_date)
    pricing_df = sqlContext.read.parquet(HDFS_PRICING_INPUT + "dt=" + run_date + "/")
    zone_df = sqlContext.read.parquet(HDFS_ZONE_LOOKUP)
    promo_df = sqlContext.read.parquet(HDFS_PROMOTIONS + "dt=" + run_date + "/")

    # Join promotions to get the raw discount before capping.
    joined = pricing_df.join(promo_df, on="sku", how="left")
    joined = joined.withColumn(
        "discount_percent",
        F.when(F.col("promo_discount_percent").isNull(), F.lit(0.0)).otherwise(
            F.col("promo_discount_percent")
        ),
    )

    # Discount cap applied inline — no test coverage, no shared utility,
    # this exact logic is copy-pasted into at least 2 other jobs on the
    # cluster per developer interview (02-dependency-analysis/ finding).
    capped = joined.withColumn(
        "discount_percent",
        F.when(F.col("discount_percent") > MAX_DISCOUNT_PERCENT, F.lit(MAX_DISCOUNT_PERCENT)).otherwise(
            F.col("discount_percent")
        ),
    )

    priced = capped.withColumn(
        "final_price", F.round(F.col("base_price") * (1 - F.col("discount_percent") / 100), 2)
    )

    with_zone = priced.join(zone_df, on="region", how="left")

    result = with_zone.select(
        "sku", "base_price", "discount_percent", "final_price", "region", "pricing_zone"
    ).withColumn("dt", F.lit(run_date))

    # NON-IDEMPOTENT: appends every run. Re-running for the same run_date
    # (e.g. after a failure and manual retry) duplicates every row for
    # that date — flagged in 07-spark-migration/07-idempotency-design.md
    # as exactly the pattern that must be fixed during migration.
    result.write.mode("append").insertInto(HIVE_OUTPUT_TABLE)

    print("pricing_nightly_batch complete for %s, %d rows written" % (run_date, result.count()))
    sc.stop()


if __name__ == "__main__":
    main()
