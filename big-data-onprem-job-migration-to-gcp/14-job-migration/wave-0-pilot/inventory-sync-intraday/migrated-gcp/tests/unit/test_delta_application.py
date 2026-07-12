from inventory_sync_intraday.transformations.delta_application import apply_deltas, compute_net_deltas


class TestComputeNetDeltas:
    def test_sums_multiple_events_for_same_item(self, spark):
        df = spark.createDataFrame(
            [("WH1", "SKU1", 5), ("WH1", "SKU1", -2), ("WH1", "SKU1", 3)],
            ["warehouse_id", "sku", "quantity_delta"],
        )
        result = compute_net_deltas(df)
        assert result.collect()[0]["net_delta"] == 6

    def test_keeps_different_items_separate(self, spark):
        df = spark.createDataFrame(
            [("WH1", "SKU1", 5), ("WH1", "SKU2", 3)],
            ["warehouse_id", "sku", "quantity_delta"],
        )
        result = compute_net_deltas(df)
        assert result.count() == 2


class TestApplyDeltas:
    def test_positive_delta_increases_quantity(self, spark):
        current = spark.createDataFrame([("WH1", "SKU1", 100)], ["warehouse_id", "sku", "on_hand_quantity"])
        deltas = spark.createDataFrame([("WH1", "SKU1", 10)], ["warehouse_id", "sku", "net_delta"])
        result = apply_deltas(current, deltas)
        assert result.collect()[0]["on_hand_quantity"] == 110

    def test_negative_delta_decreases_quantity(self, spark):
        current = spark.createDataFrame([("WH1", "SKU1", 100)], ["warehouse_id", "sku", "on_hand_quantity"])
        deltas = spark.createDataFrame([("WH1", "SKU1", -30)], ["warehouse_id", "sku", "net_delta"])
        result = apply_deltas(current, deltas)
        assert result.collect()[0]["on_hand_quantity"] == 70

    def test_new_item_with_no_current_state_starts_from_zero(self, spark):
        current = spark.createDataFrame([], "warehouse_id STRING, sku STRING, on_hand_quantity INT")
        deltas = spark.createDataFrame([("WH1", "SKU_NEW", 25)], ["warehouse_id", "sku", "net_delta"])
        result = apply_deltas(current, deltas)
        assert result.collect()[0]["on_hand_quantity"] == 25

    def test_item_with_no_delta_this_window_is_unchanged(self, spark):
        current = spark.createDataFrame([("WH1", "SKU1", 100)], ["warehouse_id", "sku", "on_hand_quantity"])
        deltas = spark.createDataFrame([], "warehouse_id STRING, sku STRING, net_delta INT")
        result = apply_deltas(current, deltas)
        assert result.collect()[0]["on_hand_quantity"] == 100
