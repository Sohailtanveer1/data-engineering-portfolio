"""
SparkSessionFactory — see 07-spark-migration/08-oop-design-patterns.md
and 07-spark-migration/examples/spark_session_factory.py (canonical source).
"""

from __future__ import annotations

from pyspark.sql import SparkSession

from dp_spark_common.config.loader import JobConfig


class SparkSessionFactory:
    _BASE_CONFIG = {
        "spark.sql.adaptive.enabled": "true",
        "spark.sql.adaptive.coalescePartitions.enabled": "true",
        "spark.sql.adaptive.skewJoin.enabled": "true",
        "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
        "spark.hadoop.fs.gs.impl": "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem",
        "spark.hadoop.google.cloud.auth.service.account.enable": "true",
    }

    @classmethod
    def create(cls, app_name: str, config: JobConfig, master: str | None = None) -> SparkSession:
        builder = SparkSession.builder.appName(app_name)
        if master is not None:
            builder = builder.master(master)

        effective_config = dict(cls._BASE_CONFIG)
        shuffle_partitions = config.get("spark.shuffle_partitions", default=None)
        if shuffle_partitions is not None:
            effective_config["spark.sql.shuffle.partitions"] = str(shuffle_partitions)

        for key, value in effective_config.items():
            builder = builder.config(key, value)

        spark = builder.getOrCreate()
        spark.sparkContext.setLogLevel("WARN")
        return spark
