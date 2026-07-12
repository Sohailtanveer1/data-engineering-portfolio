"""
Shared pytest fixtures for pricing_nightly_batch unit tests.

Per 07-spark-migration/09-unit-testing-strategy.md: a local[2] SparkSession,
no live cluster or GCP connection required.
"""

import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark():
    session = (
        SparkSession.builder.master("local[2]")
        .appName("pricing-nightly-batch-unit-tests")
        .getOrCreate()
    )
    yield session
    session.stop()
