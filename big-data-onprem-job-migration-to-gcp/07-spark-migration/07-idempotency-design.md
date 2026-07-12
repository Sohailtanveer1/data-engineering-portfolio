# Idempotency Design

**Purpose:** Make every migrated job safely re-runnable against the same
input without producing duplicate or incorrect output — a hard requirement
established as early as
[`01-discovery/questions/06-developers.md`](../01-discovery/questions/06-developers.md)
Q6, and confirmed as a gap for several jobs in
[`01-discovery/inventories/08-spark-inventory.md`](../01-discovery/inventories/08-spark-inventory.md).
**Owner:** Platform Engineering, verified per job by Data Engineering.

---

## Why idempotency is non-negotiable for this migration

Retry logic (per
[`06-logging-and-error-handling.md`](06-logging-and-error-handling.md)),
parallel-run validation (per
[`16-data-validation/`](../16-data-validation/README.md)), and cutover
rehearsal (per [`21-cutover/`](../21-cutover/README.md)) all depend on
being able to safely re-run a job multiple times against the same input.
A non-idempotent job makes every one of these safety mechanisms
dangerous instead of safe.

## Idempotent write patterns by target

| Target | Non-Idempotent Pattern (avoid) | Idempotent Pattern (required) |
|---|---|---|
| GCS/Parquet (partitioned) | Append new files to a partition on every run | Overwrite the specific partition entirely per run (`INSERT OVERWRITE`-equivalent via full partition rewrite) |
| BigQuery | `INSERT`/append on every run | `MERGE` (upsert) keyed on a natural/business key, or `WRITE_TRUNCATE` load per partition for full-partition-replacement jobs |
| Dataproc-managed Hive table | Blind `INSERT INTO` | `INSERT OVERWRITE TABLE ... PARTITION (...)` |
| External system (API push, file export) | Re-sending on retry without a de-duplication mechanism | Include an idempotency key in the request; the receiving system deduplicates, or the job checks completion state before re-sending |

## Verifying idempotency (required test for every job)

Every job's integration test suite (per
[`10-integration-testing-strategy.md`](10-integration-testing-strategy.md))
must include an explicit idempotency test:

1. Run the job against a fixed test input.
2. Capture the output (row count, checksum, or full content comparison
   depending on data size).
3. Run the job again against the identical input.
4. Assert the output is byte-for-byte/row-for-row identical to the first
   run — no duplicates, no missing rows, no changed values.

## Handling genuinely stateful/incremental jobs

For jobs that are inherently incremental (per
[`06-data-migration/02-incremental-load-strategy.md`](../06-data-migration/02-incremental-load-strategy.md)),
idempotency means: re-running the job **from the same watermark** produces
the same result — not that running it twice in immediate succession
(advancing the watermark each time) produces the same result, which would
be a misunderstanding of what idempotency means for an incremental job.
The watermark-advance-only-after-confirmed-write pattern in
[`06-data-migration/02-incremental-load-strategy.md`](../06-data-migration/02-incremental-load-strategy.md)
is what makes incremental jobs safely retryable.

## Remediating non-idempotent jobs found in Discovery

For every job flagged "No" or "Unknown" for idempotency in
[`01-discovery/inventories/08-spark-inventory.md`](../01-discovery/inventories/08-spark-inventory.md):

1. Identify the specific non-idempotent write pattern (usually a blind
   append).
2. Redesign the write per the patterns table above.
3. Confirm with the job owner whether the redesign changes behavior in any
   externally-visible way (e.g., if downstream consumers were relying on
   the append-only history for some reason) — flag and resolve any such
   dependency before proceeding, rather than silently changing behavior
   consumers depend on.
4. Add the idempotency verification test.

## Common Mistakes

- Assuming a job is idempotent because "it's always worked fine" — many
  non-idempotent jobs have simply never been re-run against the same input
  in practice, which is different from being safe to re-run.
- Fixing the write pattern but not adding the verification test — without
  the test, idempotency can silently regress in a future code change with
  nothing catching it.

## Production Notes

For Tier 1 jobs, idempotency verification is a mandatory, blocking gate
before that job can be scheduled into its migration wave in
[`14-job-migration/`](../14-job-migration/README.md) — this is not a
"nice to have" for business-critical pipelines where a retry-induced
duplicate (e.g., double-counted revenue in a finance table) has real
business consequences.
