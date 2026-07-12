# Storage Inventory

**Purpose:** Catalog HDFS directory structure, volume, and ownership so
[`05-storage-migration/`](../../05-storage-migration/README.md) can plan
GCS bucket structure, migration sequencing, and cost estimation based on
real data, not estimates.
**Owner:** Migration Program Lead, populated with Platform Engineering.
**Inputs:** `hdfs dfs -du -s -h` per top-level directory, `hdfs dfsadmin
-report`, ownership/permission listing (`hdfs dfs -ls -R` sampled, not
exhaustive for very large trees).
**Outputs:** Directly scopes [`05-storage-migration/`](../../05-storage-migration/README.md)
and [`06-data-migration/`](../../06-data-migration/README.md).
**Validation method:** Reconcile directory-level size totals against
`hdfs dfsadmin -report` cluster-wide totals — the sum of catalogued
directories should reconcile closely with total cluster usage; a large gap
indicates missing/uncatalogued directories.

---

## HDFS directory inventory

| HDFS Path | Owning Team | Data Domain | Size | File Count | Format(s) | Growth Rate (monthly) | Retention (per `04-data-retention-and-compliance.md`) | Access Pattern | Target GCS Location |
|---|---|---|---|---|---|---|---|---|---|
| `/data/pricing/` | Data Engineering | Pricing | 12 TB | 4.2M | Parquet | +300 GB/mo | 3 yr active + archive | High-frequency read (daily batch + BI) | `gs://<company>-prod-pricing/` |
| `/data/fraud/` | Fraud Engineering | Fraud | 18 TB | 9.1M | ORC, Parquet | +600 GB/mo | 7 yr | Very high-frequency read/write (hourly) | `gs://<company>-prod-fraud/` |
| `/data/finance/` | Finance Data Eng | Finance | 2 TB | 400K | Parquet | +50 GB/mo | 7 yr | Low-frequency, high-governance | `gs://<company>-prod-finance/` |
| `/data/clickstream/` | Marketing Data Eng | Marketing | 45 TB | 22M | Avro | +2 TB/mo | 13 months active | High-volume write, batch read | `gs://<company>-prod-clickstream/` |
| `/data/legacy/` | Unowned | Unknown | 3 TB | 1.1M | Mixed (CSV, SequenceFile) | Flat/no growth | Unclear — confirm | Rarely accessed | `gs://<company>-prod-archive/` or excluded pending confirmation |
| `/tmp/`, `/user/*/scratch/` | Various | N/A (scratch) | 8 TB | Varies | Mixed | Volatile | None — scratch space | Not migrated; rebuilt fresh on GCP |

_(Illustrative rows only — populate exhaustively from actual `hdfs dfs -du`
output at a directory depth that separates data domains cleanly, typically
2–3 levels deep.)_

## Permissions & ownership snapshot

| Path | POSIX/HDFS ACL Owner | Group | Ranger Policy Reference | GCP IAM Target |
|---|---|---|---|---|
| `/data/pricing/` | `svc_pricing_etl` | `pricing_team` | `ranger-policy-pricing-01` | Dedicated service account + IAM role, see [`10-security/`](../../10-security/README.md) |
| `/data/fraud/` | `svc_fraud_etl` | `fraud_team` | `ranger-policy-fraud-01` | Dedicated service account, tightly scoped |

_(Populate exhaustively — every top-level data domain directory needs a
corresponding permissions row feeding the IAM design in
`10-security/`.)_

## Total volume summary

| Metric | Value |
|---|---|
| Total HDFS capacity | _(fill in)_ |
| Total HDFS used | _(fill in)_ |
| Total file count (approx.) | _(fill in)_ |
| Replication factor | _(typically 3)_ |
| Effective unique data volume (used ÷ replication factor) | _(fill in — this, not raw "used," is the real migration transfer volume)_ |

This "effective unique data volume" figure — not the raw HDFS "used" figure
inflated by replication — is the number that should drive
[`05-storage-migration/`](../../05-storage-migration/README.md) transfer
time and Storage Transfer Service cost estimation.

## Common Mistakes

- Quoting HDFS "used" capacity as the migration transfer volume without
  dividing out the replication factor — this overstates transfer time/cost
  by roughly 3x on a typical cluster.
- Skipping `/tmp/` and scratch directories in the inventory entirely
  without an explicit decision — better to note "not migrated, rebuilt
  fresh" than to have an unexplained gap in total volume reconciliation.

## Production Notes

Directories feeding Tier 1 jobs
([`02-business-critical-jobs.md`](02-business-critical-jobs.md)) should be
prioritized for early, low-risk validation migration (e.g., a read-only
copy-and-diff exercise) well before their actual cutover wave, to surface
storage-layer surprises (encoding issues, small-file problems) with time to
fix them.
