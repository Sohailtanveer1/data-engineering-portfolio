"""
Unit tests for example_pricing_job — reference pattern.

Belongs in: a job repository's tests/unit/
See: 07-spark-migration/09-unit-testing-strategy.md

Runs with a local[2] SparkSession, no live cluster or GCP connection
required — fast, deterministic, safe to run in CI on every commit.
"""

import pytest
from pyspark.sql import SparkSession

from example_pricing_job import (
    apply_discount_cap,
    calculate_final_price,
    apply_zone_mapping,
)


@pytest.fixture(scope="module")
def spark():
    session = (
        SparkSession.builder.master("local[2]")
        .appName("unit-tests-pricing")
        .getOrCreate()
    )
    yield session
    session.stop()


class TestApplyDiscountCap:
    def test_discount_within_cap_is_unchanged(self, spark):
        df = spark.createDataFrame(
            [("SKU1", 100.0, 20.0)], ["sku", "base_price", "discount_percent"]
        )
        result = apply_discount_cap(df, max_discount_percent=40.0)
        assert result.collect()[0]["discount_percent"] == 20.0

    def test_discount_above_cap_is_capped(self, spark):
        df = spark.createDataFrame(
            [("SKU1", 100.0, 75.0)], ["sku", "base_price", "discount_percent"]
        )
        result = apply_discount_cap(df, max_discount_percent=40.0)
        assert result.collect()[0]["discount_percent"] == 40.0

    def test_zero_discount_is_unchanged(self, spark):
        df = spark.createDataFrame(
            [("SKU1", 100.0, 0.0)], ["sku", "base_price", "discount_percent"]
        )
        result = apply_discount_cap(df, max_discount_percent=40.0)
        assert result.collect()[0]["discount_percent"] == 0.0

    def test_empty_dataframe_does_not_error(self, spark):
        schema = "sku STRING, base_price DOUBLE, discount_percent DOUBLE"
        df = spark.createDataFrame([], schema)
        result = apply_discount_cap(df, max_discount_percent=40.0)
        assert result.count() == 0


class TestCalculateFinalPrice:
    def test_final_price_applies_discount_correctly(self, spark):
        df = spark.createDataFrame(
            [("SKU1", 100.0, 25.0)], ["sku", "base_price", "discount_percent"]
        )
        result = calculate_final_price(df)
        assert result.collect()[0]["final_price"] == 75.0

    def test_final_price_rounds_to_two_decimals(self, spark):
        df = spark.createDataFrame(
            [("SKU1", 99.99, 33.0)], ["sku", "base_price", "discount_percent"]
        )
        result = calculate_final_price(df)
        # 99.99 * 0.67 = 66.9933 -> rounded to 66.99
        assert result.collect()[0]["final_price"] == 66.99


class TestApplyZoneMapping:
    def test_matching_region_joins_correctly(self, spark):
        pricing_df = spark.createDataFrame(
            [("SKU1", "west")], ["sku", "region"]
        )
        zone_df = spark.createDataFrame(
            [("west", "zone_a")], ["region", "pricing_zone"]
        )
        result = apply_zone_mapping(pricing_df, zone_df)
        assert result.collect()[0]["pricing_zone"] == "zone_a"

    def test_unmatched_region_produces_null_zone_not_a_dropped_row(self, spark):
        pricing_df = spark.createDataFrame(
            [("SKU1", "unmapped_region")], ["sku", "region"]
        )
        zone_df = spark.createDataFrame(
            [("west", "zone_a")], ["region", "pricing_zone"]
        )
        result = apply_zone_mapping(pricing_df, zone_df)
        assert result.count() == 1  # left join — row preserved
        assert result.collect()[0]["pricing_zone"] is None


class TestIdempotency:
    """
    Per 07-spark-migration/07-idempotency-design.md: running the same
    transformation twice against identical input must produce identical
    output.
    """

    def test_repeated_transformation_produces_identical_output(self, spark):
        df = spark.createDataFrame(
            [("SKU1", 100.0, 50.0)], ["sku", "base_price", "discount_percent"]
        )
        first_run = calculate_final_price(apply_discount_cap(df, 40.0)).collect()
        second_run = calculate_final_price(apply_discount_cap(df, 40.0)).collect()
        assert first_run == second_run
