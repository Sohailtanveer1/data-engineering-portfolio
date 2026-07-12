"""
Zone mapping logic — joins each row's region to its pricing zone.
Extracted from the on-prem original, unchanged in behavior (left join,
preserving unmatched rows with a null pricing_zone rather than dropping
them, matching on-prem behavior exactly per the parallel-run requirement
in 14-job-migration/04-parallel-run-strategy.md).
"""

from __future__ import annotations

from pyspark.sql import DataFrame


def apply_zone_mapping(df: DataFrame, zone_lookup: DataFrame) -> DataFrame:
    """Joins each row's region to its pricing zone via a left join."""
    return df.join(zone_lookup, on="region", how="left")
