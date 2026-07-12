"""
Delta application logic — extracted from the on-prem original's inline
join/aggregate into a named, independently testable function. Behavior
is unchanged (net delta per warehouse/sku, added to current on-hand
quantity, treating missing rows on either side as zero) — the
idempotency fix lives in the orchestration layer (main.py), not here, per
07-spark-migration/07-idempotency-design.md: the transformation itself
stays a pure function; what makes the *job* idempotent is never applying
the same window's deltas twice, enforced via the control table in io/.
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def compute_net_deltas(deltas_df: DataFrame) -> DataFrame:
    """Sums quantity_delta per (warehouse_id, sku) in case a window has
    multiple WMS events for the same item."""
    return deltas_df.groupBy("warehouse_id", "sku").agg(F.sum("quantity_delta").alias("net_delta"))


def apply_deltas(current_df: DataFrame, net_deltas_df: DataFrame) -> DataFrame:
    """Applies net deltas to the current on-hand state via a full outer
    join, treating a missing row on either side as quantity/delta 0."""
    joined = current_df.join(net_deltas_df, on=["warehouse_id", "sku"], how="outer")
    return joined.withColumn(
        "on_hand_quantity",
        F.coalesce(F.col("on_hand_quantity"), F.lit(0)) + F.coalesce(F.col("net_delta"), F.lit(0)),
    ).select("warehouse_id", "sku", "on_hand_quantity")
