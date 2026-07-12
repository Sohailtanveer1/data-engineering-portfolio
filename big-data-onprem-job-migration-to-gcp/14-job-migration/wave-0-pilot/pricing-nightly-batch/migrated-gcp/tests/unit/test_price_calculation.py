from pricing_nightly_batch.transformations.price_calculation import (
    apply_discount_cap,
    calculate_final_price,
)


class TestApplyDiscountCap:
    def test_discount_within_cap_is_unchanged(self, spark):
        df = spark.createDataFrame([("SKU1", 100.0, 20.0)], ["sku", "base_price", "discount_percent"])
        result = apply_discount_cap(df, max_discount_percent=40.0)
        assert result.collect()[0]["discount_percent"] == 20.0

    def test_discount_above_cap_is_capped(self, spark):
        df = spark.createDataFrame([("SKU1", 100.0, 75.0)], ["sku", "base_price", "discount_percent"])
        result = apply_discount_cap(df, max_discount_percent=40.0)
        assert result.collect()[0]["discount_percent"] == 40.0

    def test_zero_discount_is_unchanged(self, spark):
        df = spark.createDataFrame([("SKU1", 100.0, 0.0)], ["sku", "base_price", "discount_percent"])
        result = apply_discount_cap(df, max_discount_percent=40.0)
        assert result.collect()[0]["discount_percent"] == 0.0

    def test_empty_dataframe_does_not_error(self, spark):
        schema = "sku STRING, base_price DOUBLE, discount_percent DOUBLE"
        df = spark.createDataFrame([], schema)
        result = apply_discount_cap(df, max_discount_percent=40.0)
        assert result.count() == 0


class TestCalculateFinalPrice:
    def test_final_price_applies_discount_correctly(self, spark):
        df = spark.createDataFrame([("SKU1", 100.0, 25.0)], ["sku", "base_price", "discount_percent"])
        result = calculate_final_price(df)
        assert result.collect()[0]["final_price"] == 75.0

    def test_final_price_rounds_to_two_decimals(self, spark):
        df = spark.createDataFrame([("SKU1", 99.99, 33.0)], ["sku", "base_price", "discount_percent"])
        result = calculate_final_price(df)
        assert result.collect()[0]["final_price"] == 66.99


class TestIdempotency:
    """Per 07-spark-migration/07-idempotency-design.md: running the same
    transformation twice against identical input must produce identical
    output. This is the specific bug fixed vs. the on-prem original's
    mode("append") write — see ../../on-prem-source/pricing_nightly_batch.py."""

    def test_repeated_transformation_produces_identical_output(self, spark):
        df = spark.createDataFrame([("SKU1", 100.0, 50.0)], ["sku", "base_price", "discount_percent"])
        first_run = calculate_final_price(apply_discount_cap(df, 40.0)).collect()
        second_run = calculate_final_price(apply_discount_cap(df, 40.0)).collect()
        assert first_run == second_run
