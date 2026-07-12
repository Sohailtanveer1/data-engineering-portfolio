# Job Inventory (Master)

**Purpose:** The single master list of every scheduled job on the current
platform, uniquely identified, and cross-referenced by every other
inventory in this repository. This is the spine the rest of Discovery
attaches to — SLA, criticality tier, Spark/Hive specifics, scheduler
details, and dependencies all key off the Job ID assigned here.
**Owner:** Migration Program Lead, built with Platform Engineering and
validated by Developers (per
[`questions/06-developers.md`](../questions/06-developers.md)).
**Inputs:** Scheduler configuration exports (Oozie coordinator XML, cron
tables, Airflow DAG list), developer interviews.
**Outputs:** Feeds every other inventory in this folder, and directly feeds
[`02-dependency-analysis/`](../../02-dependency-analysis/README.md) and
[`14-job-migration/`](../../14-job-migration/README.md) wave planning.
**Validation method:** Reconcile the interview-derived list against a
mechanical extraction from the scheduler (every Oozie coordinator, every
crontab entry, every Airflow DAG file) — any job present in one source and
not the other is a discrepancy that must be resolved, not ignored.

---

## Job inventory table

| Job ID | Job Name | Type (Spark/Hive/Shell/Sqoop/Other) | Owning Team | Technical Owner | Business Function | Scheduler | Schedule (cron/frequency) | Current Status | Criticality Tier | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| EX-001 | `pricing_nightly_batch` | Spark | Data Engineering | _(name)_ | Pricing | Oozie | Daily 01:00 | Active | Tier 1 | See `08-spark-inventory.md` for detail |
| EX-002 | `fraud_score_hourly` | Spark Streaming | Data Engineering | _(name)_ | Fraud | Airflow | Hourly | Active | Tier 1 | Kafka-sourced |
| EX-003 | `inventory_sync_intraday` | Spark | Supply Chain Data Eng | _(name)_ | Inventory | Cron + shell wrapper | */15 min | Active | Tier 1 | |
| EX-004 | `finance_gl_reconciliation` | Hive + Shell | Finance Data Eng | _(name)_ | Finance | Oozie | Monthly (month-end+1) | Active | Tier 1 | |
| EX-005 | `marketing_campaign_attribution` | Spark | Marketing Data Eng | _(name)_ | Marketing | Airflow | Daily 02:00 | Active | Tier 2 | |
| EX-006 | `weekly_merchandising_adhoc_report` | Hive | Merchandising Data Eng | _(name)_ | Merchandising | Cron | Weekly Monday | Active | Tier 3 | |
| EX-007 | `legacy_vendor_feed_2019` | Sqoop + Shell | Unknown | Unassigned | Unknown | Cron | Daily 03:30 | Active (unexplained) | Tier 4 (candidate) | No confirmed owner — investigate before retirement decision |
| EX-008 | `customer_360_backfill` | Spark | Data Engineering | _(name)_ | Marketing/CRM | Ad-hoc / manual | On-demand | Active | Tier 3 | Manually triggered, not on schedule |

_(Illustrative rows only — this table must be exhaustively populated from
the actual scheduler export before Discovery can gate. A migration of this
scope typically surfaces 150–600+ rows; do not consider this document
complete until every scheduled artifact on the platform has a Job ID.)_

## Job ID convention

Assign Job IDs sequentially with a short prefix as jobs are catalogued
(e.g., `JOB-0001`, `JOB-0002`...). The `EX-` prefix above denotes
illustrative example rows only — do not reuse it for real inventory
entries, to avoid confusion between example and real data during search.

## Reconciliation checklist

- [ ] Every Oozie coordinator/workflow XML has a corresponding row.
- [ ] Every crontab entry across every edge/gateway node has a
      corresponding row.
- [ ] Every Airflow DAG (if partially adopted on-prem) has a corresponding
      row.
- [ ] Every job named in a developer interview
      ([`questions/06-developers.md`](../questions/06-developers.md)) has a
      corresponding row.
- [ ] Every job named in a business interview
      ([`questions/05-business.md`](../questions/05-business.md)) has a
      corresponding row.
- [ ] No two rows describe the same underlying job (deduplicated).

## Common Mistakes

- Cataloguing only jobs found in the primary scheduler and missing jobs
  triggered by cron on individual edge nodes outside central scheduling —
  these are common in older Hadoop estates and are exactly the kind of
  thing [`02-dependency-analysis/`](../../02-dependency-analysis/README.md)
  exists to catch, but they must first appear here.
- Assuming an "Unknown" owner job (like `EX-007` above) is safe to drop —
  it may be a critical, unglamorous integration (e.g., a vendor feed) that
  nobody currently thinks about specifically because it never breaks.

## Production Notes

Jobs with "Unknown" owner or "Active (unexplained)" status must be
explicitly investigated (check output consumers via storage access logs,
check with the team that owns the closest-related business function)
before being assigned Tier 4 and dropped from migration scope — silently
dropping an unexplained-but-load-bearing job is a common cause of
production incidents weeks after cutover.
