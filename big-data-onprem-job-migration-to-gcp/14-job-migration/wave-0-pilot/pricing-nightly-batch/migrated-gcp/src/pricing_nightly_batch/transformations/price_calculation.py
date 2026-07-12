"""
Price calculation logic — the discount cap and final price computation,
extracted from the on-prem original into named, independently testable
functions. This is also the logic developer interviews confirmed is
duplicated in at least 2 other on-prem jobs (see ../../dependency-analysis.md)
— consolidating it here, and eventually promoting it into the shared
library if other migrated jobs need the same rule, per
07-spark-migration/08-oop-design-patterns.md guidance on shared utilities.
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def apply_discount_cap(df: DataFrame, max_discount_percent: float) -> DataFrame:
    """
    Caps discount_percent at max_discount_percent.

    Business rule confirmed with Merchandising during Discovery
    (01-discovery/questions/05-business.md): discounts must never exceed
    the configured cap regardless of upstream promotional input.
    """
    return df.withColumn(
        "discount_percent",
        F.when(F.col("discount_percent") > max_discount_percent, F.lit(max_discount_percent)).otherwise(
            F.col("discount_percent")
        ),
    )


def calculate_final_price(df: DataFrame) -> DataFrame:
    """Applies the (already-capped) discount to base_price, rounded to cents."""
    return df.withColumn(
        "final_price",
        F.round(F.col("base_price") * (1 - F.col("discount_percent") / 100), 2),
    )
