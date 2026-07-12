"""
inventory_sync_intraday — MIGRATED GCP version.

Compare against ../../on-prem-source/inventory_sync_intraday.py. Two
real fixes applied here beyond re-platforming, per ../migration-record.md:
  1. Idempotency via a processed-windows control table (main risk found
     in dependency analysis).
  2. An explicit negative-on-hand-quantity guard (closes two confirmed
     production incidents).
"""

from __future__ import annotations

import argparse
import logging
import sys

from dp_spark_common.config.loader import ConfigLoader
from dp_spark_common.pipeline.builder import PipelineBuilder, PipelineContext
from dp_spark_common.session.factory import SparkSessionFactory

from inventory_sync_intraday.io.readers import is_window_already_processed, read_current_state, read_deltas
from inventory_sync_intraday.io.writers import mark_window_processed, write_on_hand_state
from inventory_sync_intraday.transformations.delta_application import apply_deltas, compute_net_deltas
from inventory_sync_intraday.transformations.validation import assert_no_negative_quantities


def check_idempotency_guard(context: PipelineContext) -> PipelineContext:
    window_id = context.config.get("inventory.window_id")
    control_table = context.config.get("inventory.control_table")
    already_processed = is_window_already_processed(context.spark, control_table, window_id)
    context.metadata["already_processed"] = already_processed
    if already_processed:
        context.logger.info(
            "window_already_processed_skipping", extra={"window_id": window_id}
        )
    return context


def read_and_apply_deltas(context: PipelineContext) -> PipelineContext:
    if context.metadata.get("already_processed"):
        return context  # idempotency guard — safe no-op re-run

    window_id = context.config.get("inventory.window_id")
    deltas = read_deltas(context.spark, context.config.get("inventory.staging_path"), window_id)
    current = read_current_state(context.spark, context.config.get("inventory.on_hand_table"))

    net_deltas = compute_net_deltas(deltas)
    updated = apply_deltas(current, net_deltas)
    updated = assert_no_negative_quantities(updated)  # Terminal/Data error if violated — never retried

    context.data["updated_state"] = updated
    return context


def write_and_mark_processed(context: PipelineContext) -> PipelineContext:
    if context.metadata.get("already_processed"):
        return context

    window_id = context.config.get("inventory.window_id")
    write_on_hand_state(context.data["updated_state"], context.config.get("inventory.output_path"))
    mark_window_processed(context.spark, context.config.get("inventory.control_table"), window_id)
    return context


def main(env: str, window_id: str) -> None:
    config = ConfigLoader.load(env=env, job_config_path=f"config/{env}.yaml")
    config.values.setdefault("inventory", {})["window_id"] = window_id
    config.require_keys(
        "inventory.staging_path",
        "inventory.on_hand_table",
        "inventory.output_path",
        "inventory.control_table",
    )

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("inventory_sync_intraday")
    spark = SparkSessionFactory.create(app_name="inventory_sync_intraday", config=config)

    pipeline = (
        PipelineBuilder(spark=spark, config=config, logger=logger)
        .add_step("check_idempotency_guard", check_idempotency_guard)
        .add_step("read_and_apply_deltas", read_and_apply_deltas)
        .add_step("write_and_mark_processed", write_and_mark_processed)
        .build()
    )
    pipeline.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True)
    parser.add_argument("--window-id", required=True)
    args = parser.parse_args(sys.argv[1:])
    main(env=args.env, window_id=args.window_id)
