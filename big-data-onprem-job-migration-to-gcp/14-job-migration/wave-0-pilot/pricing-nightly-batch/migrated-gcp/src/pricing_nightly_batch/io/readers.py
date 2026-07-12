"""
I/O readers — path construction and read logic, separated from
transformation logic per 07-spark-migration/01-repository-restructuring.md.
Paths are now config-driven (per 07-spark-migration/05-configuration-management-and-secrets.md)
instead of the hardcoded HDFS URIs in the on-prem original.
"""

from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession


def read_pricing_snapshot(spark: SparkSession, input_path: str, run_date: str) -> DataFrame:
    return spark.read.parquet(f"{input_path.rstrip('/')}/dt={run_date}/")


def read_zone_lookup(spark: SparkSession, zone_lookup_path: str) -> DataFrame:
    # Not partitioned — small reference table, broadcast-joined downstream
    # per 17-performance/03-broadcast-joins.md.
    return spark.read.parquet(zone_lookup_path)


def read_promotions(spark: SparkSession, promotions_path: str, run_date: str) -> DataFrame:
    return spark.read.parquet(f"{promotions_path.rstrip('/')}/dt={run_date}/")
