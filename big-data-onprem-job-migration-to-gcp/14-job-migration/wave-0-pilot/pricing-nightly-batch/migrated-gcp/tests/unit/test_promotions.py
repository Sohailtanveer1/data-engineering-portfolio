from pricing_nightly_batch.transformations.promotions import apply_promotions


class TestApplyPromotions:
    def test_sku_with_active_promotion_gets_discount(self, spark):
        pricing_df = spark.createDataFrame([("SKU1", 100.0)], ["sku", "base_price"])
        promo_df = spark.createDataFrame([("SKU1", 20.0)], ["sku", "promo_discount_percent"])
        result = apply_promotions(pricing_df, promo_df)
        assert result.collect()[0]["discount_percent"] == 20.0

    def test_sku_with_no_promotion_gets_zero_not_null(self, spark):
        pricing_df = spark.createDataFrame([("SKU2", 50.0)], ["sku", "base_price"])
        promo_df = spark.createDataFrame([], "sku STRING, promo_discount_percent DOUBLE")
        result = apply_promotions(pricing_df, promo_df)
        row = result.collect()[0]
        assert row["discount_percent"] == 0.0
        assert row["sku"] == "SKU2"  # row preserved, left join

    def test_row_count_preserved_regardless_of_promotion_match(self, spark):
        pricing_df = spark.createDataFrame(
            [("SKU1", 100.0), ("SKU2", 50.0), ("SKU3", 75.0)], ["sku", "base_price"]
        )
        promo_df = spark.createDataFrame([("SKU1", 20.0)], ["sku", "promo_discount_percent"])
        result = apply_promotions(pricing_df, promo_df)
        assert result.count() == 3
