"""
Business-rule validation — the negative-on-hand-quantity guard, added
during migration to close a confirmed real incident (see
../../dependency-analysis.md). This did not exist in the on-prem
original at all.
"""

from __future__ import annotations

from pyspark.sql import DataFrame

from dp_spark_common.retry.decorator import DataValidationError


def assert_no_negative_quantities(df: DataFrame) -> DataFrame:
    """
    Raises DataValidationError (a Terminal/Data error per
    07-spark-migration/06-logging-and-error-handling.md — never retried)
    if any row has a negative on_hand_quantity. Returns the input
    DataFrame unchanged on success, so this can be chained inline in the
    pipeline.
    """
    negative_count = df.filter(df.on_hand_quantity < 0).count()
    if negative_count > 0:
        raise DataValidationError(
            f"{negative_count} row(s) have negative on_hand_quantity after delta "
            f"application — refusing to write. This is exactly the incident pattern "
            f"confirmed in ../../dependency-analysis.md; investigate the source "
            f"WMS delta feed for this window before retrying."
        )
    return df
