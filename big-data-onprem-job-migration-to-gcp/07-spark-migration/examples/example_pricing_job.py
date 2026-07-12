"""
example_pricing_job — A complete job assembled from the shared patterns.

Belongs in: a job repository's src/<job_name>/ (e.g. pricing_nightly_batch)
See: 07-spark-migration/01-repository-restructuring.md for full project layout

This mirrors the illustrative EX-001 `pricing_nightly_batch` job used
throughout the Discovery inventories. Business logic (transformations) is
kept separate from orchestration (main/pipeline assembly) and from I/O, so
each layer is independently testable per 07-spark-migration/09-unit-testing-strategy.md.
"""

from __future__ import annotations

import sys

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from config_loader import ConfigLoader
from job_builder import PipelineBuilder, PipelineContext
from spark_session_factory import SparkSessionFactory

# --- Transformations (business logic — pure functions over DataFrames) -----


def apply_discount_cap(df: DataFrame, max_discount_percent: float) -> DataFrame:
    """
    Caps discount_percent at max_discount_percent.

    Business rule confirmed with Merchandising during Discovery
    (01-discovery/questions/05-business.md): discounts must never exceed
    the configured cap regardless of upstream promotional input.
    """
    return df.withColumn(
        "discount_percent",
        F.when(F.col("discount_percent") > max_discount_percent, max_discount_percent)
        .otherwise(F.col("discount_percent")),
    )


def calculate_final_price(df: DataFrame) -> DataFrame:
    """Applies the (already-capped) discount to base_price."""
    return df.withColumn(
        "final_price",
        F.round(F.col("base_price") * (1 - F.col("discount_percent") / 100), 2),
    )


def apply_zone_mapping(df: DataFrame, zone_lookup: DataFrame) -> DataFrame:
    """Joins each SKU's postal-code-derived region to its pricing zone."""
    return df.join(zone_lookup, on="region", how="left")


# --- Pipeline steps (orchestration glue — thin, delegates to transformations) ---


def read_source(context: PipelineContext) -> PipelineContext:
    input_path = context.config.get("pricing.input_path")
    df = context.spark.read.parquet(input_path)
    context.data["pricing_raw"] = df
    return context


def read_zone_lookup(context: PipelineContext) -> PipelineContext:
    lookup_path = context.config.get("pricing.zone_lookup_path")
    context.data["zone_lookup"] = context.spark.read.parquet(lookup_path)
    return context


def transform_pricing(context: PipelineContext) -> PipelineContext:
    max_discount = context.config.get("pricing.discount_cap_percent")
    df = context.data["pricing_raw"]
    df = apply_discount_cap(df, max_discount_percent=max_discount)
    df = calculate_final_price(df)
    df = apply_zone_mapping(df, context.data["zone_lookup"])
    context.data["pricing_final"] = df
    return context


def write_output(context: PipelineContext) -> PipelineContext:
    output_path = context.config.get("pricing.output_path")
    run_date = context.config.get("pricing.run_date")
    # Idempotent write: overwrite the specific partition only.
    # See 07-spark-migration/07-idempotency-design.md.
    (
        context.data["pricing_final"]
        .withColumn("dt", F.lit(run_date))
        .write.mode("overwrite")
        .partitionBy("dt")
        .parquet(output_path)
    )
    return context


# --- Entry point -------------------------------------------------------------


def main(env: str, run_date: str) -> None:
    config = ConfigLoader.load(env=env, job_config_path=f"config/{env}.yaml")
    config.require_keys(
        "pricing.input_path",
        "pricing.zone_lookup_path",
        "pricing.output_path",
        "pricing.discount_cap_percent",
    )

    import logging

    logger = logging.getLogger("pricing_nightly_batch")
    spark = SparkSessionFactory.create(app_name="pricing_nightly_batch", config=config)

    pipeline = (
        PipelineBuilder(spark=spark, config=config, logger=logger)
        .add_step("read_source", read_source)
        .add_step("read_zone_lookup", read_zone_lookup)
        .add_step("transform_pricing", transform_pricing)
        .add_step("write_output", write_output)
        .build()
    )
    pipeline.run()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True)
    parser.add_argument("--run-date", required=True)
    args = parser.parse_args(sys.argv[1:])
    main(env=args.env, run_date=args.run_date)
