# Hive Metastore Migration Strategy

**Purpose:** Define how the subset of tables targeting Dataproc-Hive (per
[`04-target-architecture/05-data-warehouse-architecture.md`](../04-target-architecture/05-data-warehouse-architecture.md))
get their metadata migrated to a managed Dataproc Metastore instance.
**Owner:** Platform Engineering.

---

## Target: Dataproc Metastore (managed)

Per the target architecture decision, tables staying in a Hive-pattern
(primarily pipeline-internal staging tables) use **Dataproc Metastore**, a
fully managed Hive Metastore service — not a self-hosted MySQL-backed
Metastore replicating the current on-prem pattern (see the managed-
services-by-default principle in
[`04-target-architecture/README.md`](../04-target-architecture/README.md)).
This directly resolves pain point #2 (single, non-HA Metastore SPOF) from
[`03-current-environment/09-pain-points-and-bottlenecks.md`](../03-current-environment/09-pain-points-and-bottlenecks.md).

## Migration approach

1. **Provision Dataproc Metastore** via Terraform
   ([`13-infrastructure/`](../13-infrastructure/README.md)), one instance
   per environment (dev/qa/stage/prod), attached to the relevant Dataproc
   clusters.
2. **Export DDL from the on-prem Metastore** for every table/view/database
   targeting Dataproc-Hive, using `SHOW CREATE TABLE`/`SHOW CREATE VIEW`
   scripted across the full set (not manually per table).
3. **Translate storage locations** in the exported DDL from `hdfs://...`
   paths to the corresponding `gs://...` paths per
   [`04-target-architecture/04-storage-architecture.md`](../04-target-architecture/04-storage-architecture.md)
   zoning.
4. **Execute the translated DDL** against the target Dataproc Metastore
   instance, in dependency order (databases → base tables → views, per
   [`05-view-migration.md`](05-view-migration.md)).
5. **Validate** the Metastore catalog matches expectations — table count,
   column definitions, partition scheme — via a scripted comparison
   against the source Metastore export.

## What does NOT migrate to Dataproc Metastore

Per
[`04-target-architecture/05-data-warehouse-architecture.md`](../04-target-architecture/05-data-warehouse-architecture.md),
tables targeting BigQuery do not go through this Metastore migration path
at all — they are created directly as BigQuery tables via
[`13-infrastructure/`](../13-infrastructure/README.md) Terraform and loaded
per [`06-data-migration/`](../06-data-migration/README.md). Confirm each
table's target before applying this document's procedure, using
[`01-discovery/inventories/09-hive-inventory.md`](../01-discovery/inventories/09-hive-inventory.md)
as the authoritative per-table decision record.

## Metastore sizing and HA

Dataproc Metastore is provisioned with an HA-capable tier for `prod` (per
the DR requirements in
[`01-discovery/inventories/05-disaster-recovery-rpo-rto.md`](../01-discovery/inventories/05-disaster-recovery-rpo-rto.md)),
sized based on the actual table/partition count captured in
[`03-current-environment/04-hive-environment-assessment.md`](../03-current-environment/04-hive-environment-assessment.md)
— not a default/minimum tier assumed sufficient without checking against
the real catalog size.

## Common Mistakes

- Self-hosting a Hive Metastore on a Dataproc cluster node (technically
  possible) instead of using the managed Dataproc Metastore service — this
  reproduces the exact single-point-of-failure and operational burden
  pattern the migration is meant to eliminate.
- Migrating DDL without translating storage locations, resulting in tables
  registered in the new Metastore that still point at now-inaccessible
  `hdfs://` paths.

## Production Notes

Provision and validate the `prod` Dataproc Metastore instance well ahead
of the first table migration wave — Metastore provisioning itself is
infrequent, low-risk infrastructure work that should not be on the
critical path for any individual table's migration timeline.
