"""
I/O readers, including the idempotency control-table check.

Per 07-spark-migration/07-idempotency-design.md: for a stateful,
read-modify-write job like this one, idempotency isn't achieved by an
overwrite alone (the on-prem bug) — it requires tracking which windows
have already been applied, and skipping re-application. This mirrors the
watermark-advance-only-after-confirmed-write pattern in
06-data-migration/02-incremental-load-strategy.md, applied here at
15-minute-window granularity instead of a daily watermark.
"""

from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession


def read_deltas(spark: SparkSession, staging_path: str, window_id: str) -> DataFrame:
    return spark.read.parquet(f"{staging_path.rstrip('/')}/window={window_id}/")


def read_current_state(spark: SparkSession, on_hand_table: str) -> DataFrame:
    return spark.read.table(on_hand_table)


def is_window_already_processed(spark: SparkSession, control_table: str, window_id: str) -> bool:
    """
    Returns True if this window_id has already been successfully applied
    — the idempotency guard. A re-run for an already-processed window is
    a safe no-op, not a re-application of the same deltas.
    """
    result = spark.sql(
        f"SELECT COUNT(*) as cnt FROM {control_table} WHERE window_id = '{window_id}'"
    ).collect()
    return result[0]["cnt"] > 0
