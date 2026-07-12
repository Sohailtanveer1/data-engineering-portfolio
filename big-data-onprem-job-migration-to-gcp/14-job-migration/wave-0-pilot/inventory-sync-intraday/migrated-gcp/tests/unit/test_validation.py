import pytest

from dp_spark_common.retry.decorator import DataValidationError
from inventory_sync_intraday.transformations.validation import assert_no_negative_quantities


class TestAssertNoNegativeQuantities:
    def test_all_positive_quantities_pass_through_unchanged(self, spark):
        df = spark.createDataFrame([("WH1", "SKU1", 100), ("WH1", "SKU2", 0)], ["warehouse_id", "sku", "on_hand_quantity"])
        result = assert_no_negative_quantities(df)
        assert result.count() == 2

    def test_negative_quantity_raises_data_validation_error(self, spark):
        df = spark.createDataFrame([("WH1", "SKU1", -5)], ["warehouse_id", "sku", "on_hand_quantity"])
        with pytest.raises(DataValidationError):
            assert_no_negative_quantities(df)

    def test_single_negative_among_many_valid_rows_still_raises(self, spark):
        df = spark.createDataFrame(
            [("WH1", "SKU1", 100), ("WH1", "SKU2", -1), ("WH1", "SKU3", 50)],
            ["warehouse_id", "sku", "on_hand_quantity"],
        )
        with pytest.raises(DataValidationError):
            assert_no_negative_quantities(df)
