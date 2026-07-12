# Hive Environment Assessment

**Purpose:** Document the current Hive Metastore and HiveServer2
infrastructure — as distinct from the table/data-level detail already
captured in
[`01-discovery/inventories/09-hive-inventory.md`](../01-discovery/inventories/09-hive-inventory.md)
— feeding directly into
[`08-hive-migration/`](../08-hive-migration/README.md) metastore migration
planning.
**Owner:** Platform Engineering.
**Inputs:** `hive-site.xml`, Metastore backing database (typically
MySQL/PostgreSQL) configuration, HiveServer2 configuration.

---

## Hive Metastore configuration

| Setting | Current Value |
|---|---|
| Hive version | |
| Metastore backing database engine | _(MySQL/PostgreSQL/Derby — flag Derby immediately as a single-node, non-production pattern if found)_ |
| Metastore database size | |
| Metastore HA configured? | _(single instance vs. multiple Metastore service instances)_ |
| Metastore backing DB HA/replication configured? | |
| Total database count | |
| Total table count | |
| Total partition count (approx.) | |

## HiveServer2 configuration

| Setting | Current Value |
|---|---|
| HiveServer2 deployment mode | _(embedded / remote)_ |
| Authentication mode | _(Kerberos / LDAP / none)_ |
| Concurrent session limit | |
| Execution engine | _(MapReduce / Tez / Spark — confirm; this affects how query patterns map to the Spark/BigQuery target)_ |

## Table format and storage summary

Cross-reference with
[`01-discovery/inventories/09-hive-inventory.md`](../01-discovery/inventories/09-hive-inventory.md)
for the full per-table breakdown; summarize here:

| Format | # Tables | % of Total Storage Volume |
|---|---|---|
| Parquet | | |
| ORC | | |
| Avro | | |
| Text/CSV/SequenceFile (legacy) | | |

A high proportion of legacy text-format tables is a direct cost and
performance driver for [`06-data-migration/`](../06-data-migration/README.md)
— these should be prioritized for conversion to Parquet/ORC during
migration, not carried forward as-is.

## Metastore performance characteristics

| Question | Finding |
|---|---|
| Are there known slow queries against the Metastore itself (e.g., `SHOW PARTITIONS` on very large tables)? | |
| Is Metastore query response time a known operational pain point? | |
| Are there tables with an extremely high partition count that stress the Metastore? | |

High partition counts on individual tables are a common Hive Metastore
scaling pain point and should be flagged explicitly — the target design in
[`08-hive-migration/`](../08-hive-migration/README.md) should confirm
whether BigQuery (which handles high partition/table counts differently)
resolves this pain point for the affected tables.

## Common Mistakes

- Treating the Hive version as a single fixed fact — some estates run
  Hive via Spark's built-in Hive support (Spark's bundled Hive libraries)
  in addition to a standalone HiveServer2, and these can be on different
  effective versions.
- Missing Metastore database sizing/performance data because "it just
  works" — undocumented Metastore performance problems often only surface
  once query volume increases during migration validation/parallel-run
  activity.

## Production Notes

If the Metastore backing database is a single, non-HA MySQL/PostgreSQL
instance with no documented backup/restore test (cross-reference
[`01-discovery/inventories/05-disaster-recovery-rpo-rto.md`](../01-discovery/inventories/05-disaster-recovery-rpo-rto.md)),
flag this explicitly as a current single point of failure that the GCP
target (Dataproc Metastore, a managed service with built-in HA/backup)
should resolve — not just replicate.
