# Parallel-Run Strategy

**Purpose:** Define how a job runs simultaneously on-prem and on GCP,
comparing output, before GCP becomes the system of record — the primary
risk mitigation for cutover, referenced throughout this repository.
**Owner:** Data Engineering, per job.

---

## Parallel-run mechanics

1. The on-prem job continues running on its existing schedule, as system
   of record — no change to production behavior.
2. The migrated GCP job (built in
   [`07-spark-migration/`](../07-spark-migration/README.md), orchestrated
   by the DAG built in
   [`09-composer-migration/`](../09-composer-migration/README.md)) runs on
   the same schedule, reading from data kept in sync per
   [`05-storage-migration/04-incremental-sync-strategy.md`](../05-storage-migration/04-incremental-sync-strategy.md).
3. Both outputs are compared using the reconciliation framework from
   [`06-data-migration/07-data-reconciliation-framework.md`](../06-data-migration/07-data-reconciliation-framework.md),
   automated to run after every parallel execution, not just at the end
   of the parallel-run period.
4. GCP output is **not** consumed by any downstream system during
   parallel-run — it exists purely for comparison, isolated in its own
   GCS/BigQuery location, until cutover is approved.

## Duration by tier

Per [`02-wave-planning.md`](02-wave-planning.md), parallel-run duration
scales with tier:

| Tier | Minimum Duration | Extension Trigger |
|---|---|---|
| Tier 3 | 3-5 days (or 1 full run cycle for weekly/monthly jobs) | Any reconciliation failure resets the clock |
| Tier 2 | 5-7 days | Any reconciliation failure resets the clock |
| Tier 1 | 2-3 weeks minimum, covering at least one instance of any known edge-case period (e.g., a month-end for finance jobs) | Any reconciliation failure resets the clock; Business Owner may request extension |

## Handling reconciliation failures during parallel-run

A reconciliation failure during parallel-run is **not** a production
incident (GCP output isn't consumed yet) — it's exactly what parallel-run
exists to catch. The response is:

1. Investigate root cause using
   [`06-data-migration/07-data-reconciliation-framework.md`](../06-data-migration/07-data-reconciliation-framework.md)
   failure-handling guidance.
2. Fix the issue in the GCP job/pipeline.
3. Re-run and re-validate.
4. Reset the parallel-run duration clock — a job doesn't "bank" prior
   successful days against a later failure; the minimum duration must be
   achieved with no unresolved failures in the window.

## Cost of parallel-run

Running both platforms simultaneously has a real, budgeted cost (both
on-prem capacity continues to be consumed, and GCP resources run
redundantly) — tracked explicitly in
[`19-cost-optimization/`](../19-cost-optimization/README.md) as an
expected, time-boxed program cost, not an open-ended one. This directly
informs risk R10 in
[`00-project-overview/07-risk-register-summary.md`](../00-project-overview/07-risk-register-summary.md).

## Exiting parallel-run (cutover readiness)

A job exits parallel-run and becomes cutover-ready when:

1. The minimum duration for its tier has elapsed with zero unresolved
   reconciliation failures.
2. UAT sign-off is obtained (Tier 1/2, per
   [`20-uat/`](../20-uat/README.md)).
3. The production deployment checklist
   ([`07-production-deployment-checklist.md`](07-production-deployment-checklist.md))
   is fully satisfied.

## Common Mistakes

- Shortening parallel-run duration under schedule pressure "since it's
  looked fine for a few days" — the minimum durations exist specifically
  to catch issues that only manifest under specific conditions (e.g., a
  month-end edge case) that a short window would miss.
- Allowing downstream systems to accidentally consume GCP parallel-run
  output before cutover — enforce this via IAM/access scoping (per
  [`10-security/`](../10-security/README.md)), not just convention.

## Production Notes

For Tier 1 jobs, explicitly schedule the parallel-run window to include
at least one instance of the job's known highest-complexity period (e.g.,
month-end close for finance, a promotional event for pricing) — a
parallel-run window that only covers "normal" days doesn't fully validate
the job.
