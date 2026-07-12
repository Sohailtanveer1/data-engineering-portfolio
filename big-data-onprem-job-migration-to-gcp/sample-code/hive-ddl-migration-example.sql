-- hive-ddl-migration-example.sql
--
-- Worked example: translating a Hive external table and a dependent view
-- to their BigQuery targets, per 08-hive-migration/01-metastore-migration-strategy.md
-- and 08-hive-migration/05-view-migration.md.

-- ============================================================
-- SOURCE (on-prem Hive) — captured via SHOW CREATE TABLE
-- ============================================================
-- CREATE EXTERNAL TABLE pricing.daily_price_snapshot (
--   sku STRING,
--   base_price DOUBLE,
--   discount_percent DOUBLE,
--   region STRING
-- )
-- PARTITIONED BY (dt STRING)
-- STORED AS PARQUET
-- LOCATION 'hdfs:///data/pricing/daily_price_snapshot/';
--
-- CREATE VIEW pricing.daily_price_snapshot_summary AS
-- SELECT
--   dt,
--   region,
--   SUM(base_price * (1 - discount_percent / 100)) AS total_revenue_equivalent,
--   COUNT(*) AS sku_count
-- FROM pricing.daily_price_snapshot
-- GROUP BY dt, region;


-- ============================================================
-- TARGET (BigQuery) — per 04-target-architecture/05-data-warehouse-architecture.md
-- decision: pricing.daily_price_snapshot targets BigQuery (high BI/analyst usage)
-- ============================================================

-- Base table: native BigQuery table, partitioned and clustered.
-- Storage location translated from hdfs:// to the migrated GCS curated
-- zone per 04-target-architecture/04-storage-architecture.md — data is
-- loaded into BigQuery-managed storage via a load job (per
-- 06-data-migration/), not read as an external table, per the
-- BigQuery-native-tables decision in 08-hive-migration/02-external-vs-managed-table-migration.md.

CREATE TABLE IF NOT EXISTS `acme-data-platform-prod.pricing_prod.daily_price_snapshot`
(
  sku STRING NOT NULL,
  base_price NUMERIC,
  discount_percent NUMERIC,
  region STRING,
  dt DATE NOT NULL
)
PARTITION BY dt
CLUSTER BY region
OPTIONS (
  description = "Migrated from on-prem Hive pricing.daily_price_snapshot. See 08-hive-migration/.",
  labels = [("data_domain", "pricing"), ("criticality_tier", "1")]
);

-- Dependent view, migrated only after the base table above is confirmed
-- present and reconciled — per 08-hive-migration/05-view-migration.md
-- dependency-order requirement. SQL dialect notes:
--   - Hive's implicit DOUBLE arithmetic -> BigQuery NUMERIC, explicit
--     CAST avoided where NUMERIC arithmetic is already exact.
--   - GROUP BY column list unchanged — directly portable in this case.

CREATE VIEW IF NOT EXISTS `acme-data-platform-prod.pricing_prod.daily_price_snapshot_summary` AS
SELECT
  dt,
  region,
  SUM(base_price * (1 - discount_percent / 100)) AS total_revenue_equivalent,
  COUNT(*) AS sku_count
FROM `acme-data-platform-prod.pricing_prod.daily_price_snapshot`
GROUP BY dt, region;

-- Validation query — run per 08-hive-migration/05-view-migration.md
-- "output equivalence" requirement, comparing against the on-prem view's
-- output for the same dt/region during parallel-run.
-- SELECT * FROM `acme-data-platform-prod.pricing_prod.daily_price_snapshot_summary`
-- WHERE dt = '2026-07-12'
-- ORDER BY region;
