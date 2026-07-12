"""
SparkSessionFactory — Factory pattern reference implementation.

Belongs in: dp_spark_common/session/factory.py (shared library)
See: 07-spark-migration/08-oop-design-patterns.md

Every job constructs its SparkSession through this factory instead of
calling SparkSession.builder directly, guaranteeing consistent AQE,
serializer, and connector configuration across every job on the platform.
"""

from __future__ import annotations

from pyspark.sql import SparkSession

# The config_loader module defines JobConfig; imported here only for typing
# clarity in this reference example (avoids a hard package-layout
# dependency in this standalone example file).
try:
    from config_loader import JobConfig
except ImportError:  # pragma: no cover - typing-only fallback
    JobConfig = object  # type: ignore


class SparkSessionFactory:
    """Constructs a correctly, consistently configured SparkSession."""

    # Defaults applied to every job unless explicitly overridden via config.
    _BASE_CONFIG = {
        "spark.sql.adaptive.enabled": "true",
        "spark.sql.adaptive.coalescePartitions.enabled": "true",
        "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
        # GCS connector — required for any job reading/writing gs:// paths.
        "spark.hadoop.fs.gs.impl": "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem",
        "spark.hadoop.google.cloud.auth.service.account.enable": "true",
    }

    @classmethod
    def create(cls, app_name: str, config: "JobConfig", master: str | None = None) -> SparkSession:
        """
        Build a SparkSession for `app_name`.

        `master` is only ever set explicitly for local testing
        (e.g. "local[2]") — in production on Dataproc, Spark's own
        cluster-provided master configuration is used, so this parameter
        must be left as None in any job submitted via Dataproc.
        """
        builder = SparkSession.builder.appName(app_name)

        if master is not None:
            builder = builder.master(master)

        effective_config = dict(cls._BASE_CONFIG)

        # Allow config-driven overrides, e.g. a job with unusually large
        # shuffles can set spark.sql.shuffle.partitions in its own YAML
        # without every other job inheriting that override.
        shuffle_partitions = config.get("spark.shuffle_partitions", default=None)
        if shuffle_partitions is not None:
            effective_config["spark.sql.shuffle.partitions"] = str(shuffle_partitions)

        for key, value in effective_config.items():
            builder = builder.config(key, value)

        spark = builder.getOrCreate()
        spark.sparkContext.setLogLevel("WARN")
        return spark
