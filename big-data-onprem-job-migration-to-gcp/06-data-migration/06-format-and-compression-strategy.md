# Format & Compression Strategy

**Purpose:** Standardize on a target file format and compression codec
across the migrated platform, converting legacy formats deliberately
rather than carrying forward the format inconsistency documented in
[`01-discovery/inventories/09-hive-inventory.md`](../01-discovery/inventories/09-hive-inventory.md).
**Owner:** Data Engineering.

---

## Format decision

| Current Format | Target Format | Rationale |
|---|---|---|
| Parquet (already dominant per Hive inventory) | **Parquet** (unchanged) | Already the majority format; well-supported natively by both BigQuery and Spark; columnar layout suits the mostly-analytical query patterns identified in Discovery |
| ORC | **Parquet** (converted) | Standardizing on one columnar format simplifies tooling, monitoring, and team familiarity; Parquet has marginally broader native BigQuery/Dataproc tooling support |
| Avro | **Keep Avro** for schema-evolution-sensitive streaming/Kafka-sourced data; **Parquet** for everything else | Avro's row-oriented format and strong schema evolution support remains the better fit specifically for streaming ingestion landing zones; convert to Parquet at the curated-zone transformation step |
| Text/CSV/SequenceFile (legacy) | **Parquet** (converted, mandatory) | Directly resolves pain point #5 from [`03-current-environment/09-pain-points-and-bottlenecks.md`](../03-current-environment/09-pain-points-and-bottlenecks.md) — no legacy text-format data should exist in the curated zone |

## Compression codec

| Layer | Codec | Rationale |
|---|---|---|
| Raw/landing zone | Snappy (or source-native if already compressed, e.g., gzip from an SFTP feed) | Fast decompression, minimal CPU overhead for immediate downstream processing |
| Curated zone (Parquet) | **Snappy** as default; evaluate **Zstandard (zstd)** for large, infrequently-updated, storage-cost-sensitive tables | Snappy balances compression ratio and CPU cost well for frequently-read data; zstd offers better compression ratio at moderate additional CPU cost, worth it for large archive-adjacent tables |
| Archive zone | Zstandard (zstd) or gzip, prioritizing compression ratio over decompression speed | Archive-zone data is rarely read; optimize for storage cost, not read latency |

## Conversion approach for legacy-format tables

1. Identify every non-Parquet table from
   [`01-discovery/inventories/09-hive-inventory.md`](../01-discovery/inventories/09-hive-inventory.md).
2. During [`01-historical-data-migration-plan.md`](01-historical-data-migration-plan.md)
   backfill, read the legacy-format source and write Parquet output as
   part of the same Spark batch job — do not do a separate "convert later"
   pass, since that doubles the read/write effort.
3. Validate schema fidelity explicitly post-conversion — text/CSV sources
   in particular are prone to type-inference ambiguity (e.g., a numeric
   column with leading zeros incorrectly inferred as an integer, losing
   the leading zero) that must be caught in
   [`07-data-reconciliation-framework.md`](07-data-reconciliation-framework.md)
   validation, not assumed away.

## Schema management

Every migrated table gets an explicit, versioned schema definition (not
inferred at read time in production) — see the "no inferred schemas in
production" coding standard in the root
[`README.md`](../README.md#coding--documentation-standards) and the
detailed pattern in
[`07-spark-migration/`](../07-spark-migration/README.md).

## Common Mistakes

- Converting legacy formats to Parquet without explicit schema validation,
  silently carrying forward type-inference bugs from the source format
  into a format that looks "correct" but has quietly wrong data (e.g., a
  postal code stored as an integer, losing a leading zero).
- Applying the same compression codec uniformly regardless of access
  pattern — over-indexing on compression ratio for frequently-read
  curated-zone data adds unnecessary CPU/latency cost to every read.

## Production Notes

For any Tier 1 table converted from a legacy text/CSV format, run an
explicit column-by-column type validation between source and converted
target as part of
[`07-data-reconciliation-framework.md`](07-data-reconciliation-framework.md)
— this is the single highest-risk category of silent data corruption in
the entire data migration phase.
