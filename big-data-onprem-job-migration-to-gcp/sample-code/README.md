# sample-code — Sample Code References

## Purpose

Working code samples that don't belong inside a specific phase folder's
`examples/` subdirectory because they're cross-cutting reference material.
The primary, most extensive code examples live inside their owning
phases:

- **Spark job / shared library patterns** — see
  [`07-spark-migration/examples/`](../07-spark-migration/examples/README.md)
  (ConfigLoader, SparkSessionFactory, PipelineBuilder, retry decorator, a
  complete job, and its tests).
- **Composer DAGs** — see
  [`09-composer-migration/examples/`](../09-composer-migration/examples/README.md)
  (a production DAG and a dynamic DAG factory).

This folder holds the remaining infrastructure-adjacent code samples
referenced elsewhere that don't fit either of those.

## Owner

Platform Engineering.

## Files

| File | Referenced From |
|---|---|
| [`init-actions/install-monitoring-agent.sh`](init-actions/install-monitoring-agent.sh) | [`12-cluster-design/07-initialization-actions-and-custom-images.md`](../12-cluster-design/07-initialization-actions-and-custom-images.md) |
| [`hive-ddl-migration-example.sql`](hive-ddl-migration-example.sql) | [`08-hive-migration/01-metastore-migration-strategy.md`](../08-hive-migration/01-metastore-migration-strategy.md), [`08-hive-migration/05-view-migration.md`](../08-hive-migration/05-view-migration.md) |
