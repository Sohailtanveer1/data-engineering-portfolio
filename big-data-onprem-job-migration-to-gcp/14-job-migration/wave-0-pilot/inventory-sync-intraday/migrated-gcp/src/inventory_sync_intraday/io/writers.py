"""
I/O writers — writes the updated on-hand state, then marks the window as
processed in the control table. The window is only marked processed
AFTER the state write is confirmed successful — advancing the marker
before the write would risk marking a window "done" whose data never
actually landed, per the same principle in
06-data-migration/02-incremental-load-strategy.md.
"""

from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession


def write_on_hand_state(df: DataFrame, output_path: str) -> None:
    # Full-state overwrite is intentional here (this table represents
    # current state, not an append-only log) — what makes the JOB
    # idempotent is the control-table guard in main.py, not this write
    # mode, since re-running against the same recomputed state would
    # itself be safe; the risk was re-APPLYING deltas, not re-writing
    # the same recomputed result.
    df.write.mode("overwrite").parquet(output_path)


def mark_window_processed(spark: SparkSession, control_table: str, window_id: str) -> None:
    spark.sql(
        f"INSERT INTO {control_table} (window_id, processed_at) "
        f"VALUES ('{window_id}', current_timestamp())"
    )
