# Incremental Sync Strategy

**Purpose:** Define how GCS is kept current with ongoing changes to HDFS
during the parallel-run period between a data domain's initial bulk
migration and its job's final cutover — since the source platform remains
live and actively written to throughout the migration program (per
constraint C7 in
[`00-project-overview/06-assumptions-and-constraints.md`](../00-project-overview/06-assumptions-and-constraints.md)).
**Owner:** Platform Engineering.
**Inputs:** Initial bulk migration completed per
[`02-distcp-migration-procedure.md`](02-distcp-migration-procedure.md) or
[`03-storage-transfer-service-procedure.md`](03-storage-transfer-service-procedure.md);
the job's write pattern from
[`01-discovery/inventories/08-spark-inventory.md`](../01-discovery/inventories/08-spark-inventory.md)
(how frequently and how the on-prem job writes new data).

---

## Why incremental sync is required

A data domain's storage migration typically happens before its owning
job's final cutover — but the on-prem job keeps running and writing new
data (per the charter, the on-prem cluster must remain fully operational
for any job not yet migrated). Without incremental sync, GCS would fall
increasingly out of date, making parallel-run validation
([`16-data-validation/`](../16-data-validation/README.md)) meaningless
since it would be comparing against stale data.

## Sync mechanism per scenario

| Scenario | Sync Mechanism | Frequency |
|---|---|---|
| Domain migrated via DistCp, incremental sync also via DistCp | `hadoop distcp -update` re-run on a schedule | Matches the job's write cadence (e.g., daily for `pricing`, hourly for `fraud`) |
| Domain migrated via STS, incremental sync also via STS | Scheduled STS transfer job with `--overwrite-when=different` | Same as above |
| Very high-frequency writes (e.g., intraday `inventory_sync_intraday`, every 15 min) | Consider a dual-write pattern instead — modify the on-prem job to write to both HDFS and GCS directly for the parallel-run window, if job modification is feasible without disrupting the (not-yet-migrated) production path | Real-time / per-write |

For most Tier 2/3 domains with daily or less-frequent writes, a scheduled
DistCp/STS incremental sync (daily or matching the job's own schedule) is
sufficient and simpler than a dual-write pattern. Reserve dual-write for
genuinely high-frequency Tier 1 domains where sync lag itself would
invalidate validation.

## Sync lag monitoring

| Metric | Threshold | Action if Breached |
|---|---|---|
| Time since last successful sync | > 2x the job's write frequency | Alert Platform Engineering; investigate before relying on GCS data for validation |
| File count / size delta between HDFS and GCS (post-sync) | Any unexplained delta beyond in-flight writes | Investigate before validation proceeds |

Configure this monitoring via
[`18-monitoring/`](../18-monitoring/README.md), not as a manual, ad-hoc
check — sync lag is exactly the kind of quietly-degrading process that
needs automated detection, per the "no silent failures" principle applied
throughout this repository.

## When incremental sync ends

Incremental sync for a data domain ends only after:

1. The domain's owning job(s) have fully cut over (see
   [`14-job-migration/`](../14-job-migration/README.md)).
2. [`16-data-validation/`](../16-data-validation/README.md) has confirmed
   final reconciliation.
3. The on-prem source is confirmed no longer being written to by any
   remaining job.

Do not disable incremental sync early "since the job looks stable" — wait
for the explicit gate above, since a premature sync stop can silently
reintroduce a gap if any residual on-prem write path is still active
(e.g., a downstream job or manual process not yet accounted for).

## Common Mistakes

- Setting up incremental sync once and never monitoring it — sync jobs can
  silently fail (credential expiry, network blip) and nobody notices until
  a validation discrepancy surfaces much later.
- Ending incremental sync immediately at cutover instead of maintaining it
  through the full hypercare rollback window (see
  [`07-rollback-procedure.md`](07-rollback-procedure.md) and
  [`22-hypercare/`](../22-hypercare/README.md)) — if a rollback to on-prem
  is needed during hypercare, having sync still active simplifies
  reconciling any data written during the brief post-cutover, pre-rollback
  window.

## Production Notes

For Tier 1 domains, size incremental sync frequency to comfortably beat
the job's actual write cadence, not just match it exactly — a small buffer
avoids validation runs racing against an in-progress sync.
