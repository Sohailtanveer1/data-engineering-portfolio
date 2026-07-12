# Job Dependency Card — `inventory_sync_intraday`

Filled in using
[`02-dependency-analysis/templates/02-job-dependency-card-template.md`](../../../02-dependency-analysis/templates/02-job-dependency-card-template.md)
against the real on-prem source in
[`on-prem-source/`](on-prem-source/).

**Job Name:** `inventory_sync_intraday`
**Type:** Spark (PySpark, Spark 2.4.8)
**Criticality Tier:** Tier 1 — feeds storefront inventory availability,
per
[`01-discovery/inventories/02-business-critical-jobs.md`](../../../01-discovery/inventories/02-business-critical-jobs.md)
criterion 1.
**Card completed by:** Migration pilot **Date:** 2026-07-12

---

## Upstream dependencies

| Category | Detail | Source | Confirmed via |
|---|---|---|---|
| Data input | WMS quantity-delta staging, partitioned by 15-min window | `hdfs://.../data/inventory/wms_delta_staging/window=<id>/` | Static code analysis |
| Data input | Current on-hand state (read-modify-write) | `inventory.on_hand_by_warehouse` (Hive) | Static code analysis |
| Shared library/JAR | None | N/A | Static code analysis |
| External system | WMS, indirectly — via Kafka topic landed to HDFS by a separate ingestion job (out of this job's own scope, in scope of that ingestion job's own dependency card) | N/A | [`01-discovery/inventories/07-application-inventory.md`](../../../01-discovery/inventories/07-application-inventory.md) |

## Downstream consumers

| Consumer | Type | Criticality | Confirmed via |
|---|---|---|---|
| `inventory.on_hand_by_warehouse` (Hive table) | Data | Tier 1 | Static code analysis |
| Storefront inventory availability feed | Job | Tier 1 | [`01-discovery/questions/05-business.md`](../../../01-discovery/questions/05-business.md) |
| `pricing_nightly_batch` — informal downstream timing dependency (assumed complete by 01:00) | Job | Tier 1 | Confirmed reciprocally from [`pricing-nightly-batch/dependency-analysis.md`](../pricing-nightly-batch/dependency-analysis.md) |

## Scheduler / workflow context

- **Triggered by:** Time-based, **cron directly** (not Oozie) — every 15
  minutes, per [`on-prem-source/crontab-entry.txt`](on-prem-source/crontab-entry.txt).
- **This is itself a Discovery finding worth flagging**: this job was not
  registered in the central Oozie scheduler at all and was only found via
  the mandatory per-node crontab sweep in
  [`02-dependency-analysis/methodology/04-shell-script-and-cron-dependencies.md`](../../../02-dependency-analysis/methodology/04-shell-script-and-cron-dependencies.md)
  — exactly the kind of "shadow" scheduled job that inventory relying on
  Oozie alone would have missed entirely.
- **Downstream job(s):** `pricing_nightly_batch` assumes this job's last
  run of the prior day completed before 01:00 (see reciprocal finding in
  that job's dependency card).
- **Conditional/branching logic:** None.

## Technical debt / risk flags

- [x] Hardcoded paths/hostnames found
- [x] Uses deprecated Spark APIs (`SparkContext`/`SQLContext`)
- [x] **Not idempotent** — full-table overwrite recomputed from a
      read-modify-write against current state; a re-run after a partial
      failure can silently apply deltas twice or against stale state
- [x] **No alerting on failure at all** — a real, confirmed operational
      gap (not hypothetical), per
      [`01-discovery/questions/07-operations.md`](../../../01-discovery/questions/07-operations.md)
- [x] No negative-on-hand-quantity guard — confirmed as having caused two
      real incidents in the last 6 months per operations interview
- [ ] Depends on NFS mount — no
- [x] Job exists outside the central scheduler's visibility ("shadow"
      cron job) — ownership confirmed with Supply Chain Data Engineering,
      not orphaned, just undocumented

## Validation status

- [x] Confirmed via static code analysis
- [x] Confirmed via a second technique (operations interview corroborating
      the missing-alerting and negative-quantity incident history)
- [x] Reviewed with job owner (Supply Chain Data Engineering)

## Migration readiness note

Ready to migrate. Two fixes are mandatory, not optional, given confirmed
production incident history: idempotent write semantics and a
negative-quantity guard implemented as an explicit business-rule
validation check. See
[`migration-record.md`](migration-record.md).
