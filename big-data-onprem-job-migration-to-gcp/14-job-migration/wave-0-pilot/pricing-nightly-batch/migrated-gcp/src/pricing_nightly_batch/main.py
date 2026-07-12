"""
pricing_nightly_batch — MIGRATED GCP version.

Entry point is deliberately thin: it assembles the pipeline from
independently-tested transformation and I/O functions and runs it. All
business logic lives in transformations/, all I/O lives in io/ — see
07-spark-migration/01-repository-restructuring.md.

Compare against ../../on-prem-source/pricing_nightly_batch.py — same
business outcome (validated via parallel-run,
14-job-migration/04-parallel-run-strategy.md), rebuilt on the shared
platform patterns. Full list of what changed and why is in
../migration-record.md.
"""

from __future__ import annotations

import argparse
import logging
import sys

from dp_spark_common.config.loader import ConfigLoader
from dp_spark_common.pipeline.builder import PipelineBuilder, PipelineContext
from dp_spark_common.session.factory import SparkSessionFactory

from pricing_nightly_batch.io.readers import read_pricing_snapshot, read_promotions, read_zone_lookup
from pricing_nightly_batch.io.writers import write_pricing_output
from pricing_nightly_batch.transformations.price_calculation import (
    apply_discount_cap,
    calculate_final_price,
)
from pricing_nightly_batch.transformations.promotions import apply_promotions
from pricing_nightly_batch.transformations.zone_mapping import apply_zone_mapping


def read_source(context: PipelineContext) -> PipelineContext:
    run_date = context.config.get("pricing.run_date")
    input_path = context.config.get("pricing.input_path")
    context.data["pricing_raw"] = read_pricing_snapshot(context.spark, input_path, run_date)
    return context


def read_reference_data(context: PipelineContext) -> PipelineContext:
    run_date = context.config.get("pricing.run_date")
    context.data["zone_lookup"] = read_zone_lookup(context.spark, context.config.get("pricing.zone_lookup_path"))
    context.data["promotions"] = read_promotions(
        context.spark, context.config.get("pricing.promotions_path"), run_date
    )
    return context


def transform_pricing(context: PipelineContext) -> PipelineContext:
    max_discount = context.config.get("pricing.discount_cap_percent")

    df = apply_promotions(context.data["pricing_raw"], context.data["promotions"])
    df = apply_discount_cap(df, max_discount_percent=max_discount)
    df = calculate_final_price(df)
    df = apply_zone_mapping(df, context.data["zone_lookup"])

    context.data["pricing_final"] = df.select(
        "sku", "base_price", "discount_percent", "final_price", "region", "pricing_zone"
    )
    return context


def write_output(context: PipelineContext) -> PipelineContext:
    run_date = context.config.get("pricing.run_date")
    output_path = context.config.get("pricing.output_path")
    write_pricing_output(context.data["pricing_final"], output_path, run_date)
    return context


def main(env: str, run_date: str) -> None:
    config = ConfigLoader.load(env=env, job_config_path=f"config/{env}.yaml")
    config.values.setdefault("pricing", {})["run_date"] = run_date
    config.require_keys(
        "pricing.input_path",
        "pricing.zone_lookup_path",
        "pricing.promotions_path",
        "pricing.output_path",
        "pricing.discount_cap_percent",
    )

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("pricing_nightly_batch")
    spark = SparkSessionFactory.create(app_name="pricing_nightly_batch", config=config)

    pipeline = (
        PipelineBuilder(spark=spark, config=config, logger=logger)
        .add_step("read_source", read_source)
        .add_step("read_reference_data", read_reference_data)
        .add_step("transform_pricing", transform_pricing)
        .add_step("write_output", write_output)
        .build()
    )
    pipeline.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True)
    parser.add_argument("--run-date", required=True)
    args = parser.parse_args(sys.argv[1:])
    main(env=args.env, run_date=args.run_date)
