# Execution Steps Per Job (Standard Runbook)

**Purpose:** The single, standard sequence every job follows from wave
assignment to production cutover — tying together every phase folder's
per-job procedure into one ordered checklist.
**Owner:** Data/Platform Engineering (executor), Migration Program Lead
(tracks).

---

## Standard sequence

1. **Confirm wave assignment and dependency readiness** — per
   [`01-priority-matrix.md`](01-priority-matrix.md) and
   [`02-wave-planning.md`](02-wave-planning.md); all upstream dependencies
   already migrated or in the same wave with correct sequencing.
2. **Storage migration** — per
   [`05-storage-migration/08-migration-execution-checklist.md`](../05-storage-migration/08-migration-execution-checklist.md),
   if not already complete for this job's data domain.
3. **Data migration** — per
   [`06-data-migration/08-migration-execution-runbook.md`](../06-data-migration/08-migration-execution-runbook.md).
4. **Hive migration** (if applicable) — per
   [`08-hive-migration/07-execution-runbook.md`](../08-hive-migration/07-execution-runbook.md).
5. **Spark job migration** — repository restructuring, packaging,
   idempotency, testing per
   [`07-spark-migration/README.md`](../07-spark-migration/README.md) and
   its constituent documents.
6. **Composer DAG build** — per
   [`09-composer-migration/`](../09-composer-migration/README.md).
7. **Security review** — per
   [`10-security/08-execution-and-review-checklist.md`](../10-security/08-execution-and-review-checklist.md).
8. **Integration testing** — per
   [`15-testing/`](../15-testing/README.md).
9. **Parallel-run** — per
   [`04-parallel-run-strategy.md`](04-parallel-run-strategy.md), for the
   tier-appropriate duration.
10. **UAT sign-off** (Tier 1/2) — per
    [`20-uat/`](../20-uat/README.md).
11. **Production deployment** — per
    [`07-production-deployment-checklist.md`](07-production-deployment-checklist.md)
    and [`21-cutover/`](../21-cutover/README.md).
12. **Hypercare monitoring** — per
    [`22-hypercare/`](../22-hypercare/README.md), for the defined
    post-cutover stabilization period.
13. **Tracker updated to "Complete"** — per
    [`03-migration-tracker.md`](03-migration-tracker.md).

## Step gating

Each step above is a **hard gate** — step N+1 does not begin until step N
is genuinely complete (not "mostly done" or "should be fine"). This
sequence is deliberately linear per job, even though different jobs within
a wave can progress through it in parallel with each other.

## Time estimation guidance

| Job Complexity | Rough Total Duration (Steps 1-11, excluding parallel-run wait time) |
|---|---|
| Simple (Tier 3, few dependencies, no Hive migration needed) | 1-2 weeks |
| Moderate (Tier 2, some dependencies, Hive tables involved) | 2-4 weeks |
| Complex (Tier 1, many dependencies, UDFs, views) | 4-8 weeks |

These are planning estimates for wave scheduling, not commitments — actual
duration depends on what Discovery/dependency analysis reveals for each
specific job.

## Common Mistakes

- Running steps out of sequence to "save time" (e.g., building the DAG
  before the Spark job is fully tested) — this creates rework when an
  earlier step's findings require changes that ripple into already-
  completed later steps.
- Treating this runbook as advisory rather than mandatory for "simple"
  jobs — the sequence protects against exactly the mistakes that seem
  unlikely on a simple job right up until they happen.

## Production Notes

For Tier 1 jobs, hold a brief go/no-go review at the transition between
step 9 (parallel-run) and step 10 (UAT) — this is the natural checkpoint
where the Migration Program Lead, Business Owner, and Platform Engineering
Lead should explicitly confirm readiness to proceed, not just let the
process auto-advance.
