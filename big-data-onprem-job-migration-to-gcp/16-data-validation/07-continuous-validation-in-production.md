# Continuous Validation in Production

**Purpose:** Define how the validation framework keeps running after a
job's migration is complete and it's no longer in parallel-run — because
data quality drift is an ongoing risk, not just a migration-day risk.
**Owner:** Data Engineering, integrated with
[`18-monitoring/`](../18-monitoring/README.md).

---

## What changes after cutover

During parallel-run, validation compares GCP output against a live
on-prem source. After cutover (on-prem is no longer system of record,
eventually decommissioned per
[`05-storage-migration/07-rollback-procedure.md`](../05-storage-migration/07-rollback-procedure.md)),
continuous validation shifts to:

1. **Internal consistency checks** — duplicate detection, null checks,
   business rule validation — run against GCP data alone, no longer
   requiring an on-prem comparison point.
2. **Trend-based anomaly detection** — comparing today's aggregates
   against a rolling historical baseline (e.g., "today's row count is
   more than 3 standard deviations from the trailing 30-day average") to
   catch unexpected shifts even without an external comparison source.
3. **Cross-table consistency checks** — for tables with a known
   relationship (e.g., every fulfilled order in `inventory.orders` should
   have a corresponding entry in `finance.gl_entries`), validating the
   relationship holds continuously.

## Validation schedule post-cutover

| Job Tier | Continuous Validation Frequency |
|---|---|
| Tier 1 | After every job run (matching the job's own schedule) |
| Tier 2 | Daily, regardless of job run frequency |
| Tier 3 | Weekly |

## Integration with monitoring and alerting

A continuous validation failure is treated as a production incident,
routed through the same alerting path as any other job failure (per
[`09-composer-migration/05-monitoring-retries-and-alerts.md`](../09-composer-migration/05-monitoring-retries-and-alerts.md)
and
[`18-monitoring/`](../18-monitoring/README.md)) — data quality issues
deserve the same operational rigor as a job execution failure, not
lesser treatment as a "just data" concern.

## Feeding back into hypercare

During [`22-hypercare/`](../22-hypercare/README.md), continuous validation
results are reviewed with elevated attention (part of the daily
stand-down review) — any anomaly during this period is investigated with
priority, since hypercare exists specifically to catch issues the standard
process might otherwise take longer to surface.

## Common Mistakes

- Disabling validation once a job exits parallel-run, treating validation
  as a migration-only activity — this is precisely the gap this document
  exists to close.
- Setting anomaly detection thresholds too tightly immediately post-
  cutover, before a realistic production baseline has been established,
  causing alert fatigue from false positives in the early days.

## Production Notes

For every Tier 1 job, explicitly transition continuous validation
ownership from the migration team to the standing operations team as part
of the [`22-hypercare/`](../22-hypercare/README.md) handover — validation
that "everyone assumes someone else owns" after the migration team moves
on to the next wave is a common way for this capability to quietly stop
being maintained.
