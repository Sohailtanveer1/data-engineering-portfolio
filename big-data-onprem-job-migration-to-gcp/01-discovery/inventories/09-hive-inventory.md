# Hive Inventory

**Purpose:** Catalog every Hive database, table, view, and UDF so
[`08-hive-migration/`](../../08-hive-migration/README.md) can decide, per
table, whether it migrates to BigQuery, Dataproc-managed Hive Metastore, or
is retired — and so no table is silently missed.
**Owner:** Migration Program Lead, populated with Data Engineering.
**Inputs:** Hive Metastore direct query (`SHOW DATABASES`, `SHOW TABLES`,
`DESCRIBE FORMATTED`), query logs for usage frequency.
**Outputs:** Directly scopes [`08-hive-migration/`](../../08-hive-migration/README.md).
**Validation method:** Pull the actual Metastore catalog programmatically
(via `metastore` DB query or Hive CLI scripting) rather than relying on a
manually maintained data dictionary, which is very often stale in
Hadoop estates of this age.

---

## Hive database/table inventory

| Database | Table/View | Type (Managed/External/View) | Format | Partitioned By | Approx. Row Count | Approx. Size | Last Query Date | Query Frequency (90d) | Consumers | Target on GCP |
|---|---|---|---|---|---|---|---|---|---|---|
| `pricing` | `daily_price_snapshot` | External | Parquet | `dt` (date) | 2.1B | 4.2 TB | Yesterday | Daily (automated) | `pricing_nightly_batch`, BI dashboards | BigQuery (analytical, high query frequency) |
| `fraud` | `txn_feature_scores` | Managed | ORC | `dt`, `hour` | 8.4B | 6.8 TB | Today | Hourly (automated) | `fraud_score_hourly`, fraud service | BigQuery |
| `finance` | `gl_reconciliation_monthly` | External | Parquet | `fiscal_period` | 12M | 40 GB | Last month-end | Monthly | `finance_gl_reconciliation` | BigQuery (small, high governance need) |
| `merchandising` | `weekly_adhoc_report_view` | View | N/A (view) | N/A | N/A | N/A | Last week | Weekly | Merchandising analysts | Recreate as BigQuery view over migrated base tables |
| `legacy` | `vendor_feed_2019_raw` | External | Text/CSV | None | 4M | 1.1 GB | 3 years ago | Never in 90d | None found | Candidate for archival-only migration, not active re-platforming |

_(Illustrative rows only — populate exhaustively via Metastore catalog
extraction; a platform of this description typically has 300–1000+ tables
across all databases.)_

## UDF inventory

| UDF Name | Language | Used By (databases/tables) | Purpose | Migration Path |
|---|---|---|---|---|
| `mask_pii` | Java | `fraud`, `pricing` | Custom PII masking logic | Reimplement as BigQuery SQL UDF or Spark UDF depending on target; must preserve exact masking behavior — see [`08-hive-migration/`](../../08-hive-migration/README.md) |
| `geo_zone_lookup` | Java | `pricing`, `inventory` | Maps postal code to internal pricing zone | Reimplement; validate lookup table is also migrated |

_(Illustrative — every custom UDF found in the Metastore or referenced in
job code must be catalogued; UDFs are a common silent-breakage point since
they have no direct BigQuery equivalent by default.)_

## Findings to summarize once complete

- **"Zombie" tables** — tables with no query activity in the trailing 90
  (or better, 365) days. These are strong retirement candidates, reducing
  migration scope, but must be confirmed with the owning team before being
  dropped (a table might be legitimately queried only at year-end).
- **Format distribution** — Parquet/ORC/Avro/Text mix; text/CSV-format
  tables need explicit conversion planning in
  [`06-data-migration/`](../../06-data-migration/README.md).
- **Partition scheme consistency** — tables with no partitioning at large
  scale are a performance red flag for BigQuery/Dataproc target design in
  [`08-hive-migration/`](../../08-hive-migration/README.md) and
  [`17-performance/`](../../17-performance/README.md).
- **Per-table target decision** (BigQuery vs. Dataproc Hive Metastore) —
  driven by query pattern (BI/analytical → BigQuery; Spark-job-internal,
  high-mutation → possibly stay Hive-pattern on Dataproc). Documented
  formally in [`08-hive-migration/`](../../08-hive-migration/README.md).

## Common Mistakes

- Relying on a stale internal wiki data dictionary instead of querying the
  live Metastore — table structure and ownership both drift from
  documentation over time.
- Migrating every table to BigQuery by default without evaluating whether
  some workloads are better served by Dataproc-managed Hive (e.g.,
  extremely high-mutation-rate internal staging tables).

## Production Notes

Give extra scrutiny to any table feeding `pricing`, `fraud`, or `finance`
databases — schema or semantic drift during migration in these domains has
direct business impact, not just an analytics inconvenience.
