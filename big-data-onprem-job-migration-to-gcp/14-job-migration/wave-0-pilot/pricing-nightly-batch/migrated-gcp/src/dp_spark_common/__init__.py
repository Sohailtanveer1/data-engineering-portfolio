"""
dp_spark_common — vendored copy of the shared Spark library for this pilot.

In production this package is published independently and consumed as a
pinned dependency (see
07-spark-migration/04-packaging-and-dependency-management.md) — it is
vendored directly into this pilot job's repo only so the pilot is a
single, self-contained, runnable unit during Wave 0. Source of truth for
the patterns below is 07-spark-migration/examples/.
"""
