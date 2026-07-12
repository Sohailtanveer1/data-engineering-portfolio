"""
Promotion-application logic — extracted from the inline join in the
on-prem original (../../on-prem-source/pricing_nightly_batch.py) into a
named, independently testable transformation.
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def apply_promotions(pricing_df: DataFrame, promotions_df: DataFrame) -> DataFrame:
    """
    Left-joins active promotions onto the pricing snapshot by SKU.
    A SKU with no active promotion gets discount_percent = 0, not null —
    this null-to-zero coalescing was implicit and easy to miss in the
    on-prem version's inline `F.when(...isNull()...)`; made an explicit,
    named, tested step here.
    """
    joined = pricing_df.join(promotions_df, on="sku", how="left")
    return joined.withColumn(
        "discount_percent",
        F.when(F.col("promo_discount_percent").isNull(), F.lit(0.0)).otherwise(
            F.col("promo_discount_percent")
        ),
    )
