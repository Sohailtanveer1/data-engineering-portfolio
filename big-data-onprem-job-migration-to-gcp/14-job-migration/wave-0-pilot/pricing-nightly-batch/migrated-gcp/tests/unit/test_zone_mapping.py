from pricing_nightly_batch.transformations.zone_mapping import apply_zone_mapping


class TestApplyZoneMapping:
    def test_matching_region_joins_correctly(self, spark):
        pricing_df = spark.createDataFrame([("SKU1", "west")], ["sku", "region"])
        zone_df = spark.createDataFrame([("west", "zone_a")], ["region", "pricing_zone"])
        result = apply_zone_mapping(pricing_df, zone_df)
        assert result.collect()[0]["pricing_zone"] == "zone_a"

    def test_unmatched_region_produces_null_zone_not_a_dropped_row(self, spark):
        pricing_df = spark.createDataFrame([("SKU1", "unmapped_region")], ["sku", "region"])
        zone_df = spark.createDataFrame([("west", "zone_a")], ["region", "pricing_zone"])
        result = apply_zone_mapping(pricing_df, zone_df)
        assert result.count() == 1
        assert result.collect()[0]["pricing_zone"] is None
