"""
I/O writers — idempotent output write.

Fixes the non-idempotent `mode("append")` bug from the on-prem original
(../../on-prem-source/pricing_nightly_batch.py) per
07-spark-migration/07-idempotency-design.md: overwrite exactly the target
partition, never append, so a re-run for the same run_date is safe.
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def write_pricing_output(df: DataFrame, output_path: str, run_date: str) -> None:
    (
        df.withColumn("dt", F.lit(run_date))
        .write.mode("overwrite")
        .option("partitionOverwriteMode", "dynamic")  # overwrite only the dt=run_date partition
        .partitionBy("dt")
        .parquet(output_path)
    )
