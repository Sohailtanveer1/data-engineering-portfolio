# Integration Testing Strategy

**Purpose:** Define how a full job pipeline (orchestration, I/O, and
transformation logic together) is tested end-to-end against real (but
non-production) GCS/BigQuery resources, before that job is considered
ready for parallel-run validation in
[`16-data-validation/`](../16-data-validation/README.md).
**Owner:** Platform Engineering + QA, executed in the `qa` environment per
[`04-target-architecture/02-landing-zone-and-project-structure.md`](../04-target-architecture/02-landing-zone-and-project-structure.md).

---

## What integration tests cover that unit tests don't

| Concern | Unit Test | Integration Test |
|---|---|---|
| Transformation logic correctness | Yes | No (already covered) |
| Full pipeline wiring (steps run in correct order, context passed correctly) | No | Yes |
| Actual read from GCS/BigQuery (real connector behavior, real schema enforcement) | No | Yes |
| Actual write to target, including idempotency verification | No | Yes |
| Dataproc submission mechanics (cluster creation, job submission via the real operators) | No | Partial — see [`15-testing/`](../15-testing/README.md) for full end-to-end DAG testing, which also covers this |
| Configuration loading against real Secret Manager/Composer Variables | No | Yes |

## Test environment

Integration tests run against the `qa` GCP project (per
[`04-target-architecture/02-landing-zone-and-project-structure.md`](../04-target-architecture/02-landing-zone-and-project-structure.md)),
using:

- A small, real (or realistically-shaped, masked/synthetic) dataset loaded
  into `qa` GCS buckets/BigQuery datasets — not production data.
- A short-lived, small Dataproc cluster or Dataproc Serverless batch,
  created and torn down as part of the test run (mirroring the real
  submission pattern from
  [`03-dataproc-submission-patterns.md`](03-dataproc-submission-patterns.md)).

## Required test cases per job

1. **Happy path end-to-end** — realistic input produces expected output,
   verified via the reconciliation-style checks from
   [`06-data-migration/07-data-reconciliation-framework.md`](../06-data-migration/07-data-reconciliation-framework.md)
   applied to the small test dataset.
2. **Idempotency verification** — run the job twice against identical
   input, confirm identical output (per
   [`07-idempotency-design.md`](07-idempotency-design.md) requirement).
3. **Missing/malformed input handling** — confirm the job fails clearly
   and per its error classification (per
   [`06-logging-and-error-handling.md`](06-logging-and-error-handling.md)),
   not silently producing incomplete output.
4. **Configuration failure handling** — confirm the job fails fast on
   missing required configuration (per
   [`05-configuration-management-and-secrets.md`](05-configuration-management-and-secrets.md)).
5. **Empty input handling** — confirm the job handles a zero-row input
   partition gracefully (a surprisingly common edge case that breaks
   naive Spark code, e.g., division-by-zero in an aggregate calculation
   over an empty DataFrame).

## Automation and CI integration

Integration tests run automatically in
[`ci-cd/`](../ci-cd/README.md) on every merge to the release branch,
before a job package version is published to the artifact store per
[`04-packaging-and-dependency-management.md`](04-packaging-and-dependency-management.md)
— a version that fails integration tests is never published as a
deployable artifact.

## Relationship to parallel-run validation

Integration tests prove a job **works correctly in isolation** against
controlled test data. They are a prerequisite for, but not a substitute
for, the parallel-run validation in
[`16-data-validation/`](../16-data-validation/README.md), which proves the
job produces **the same result as its on-prem counterpart against real
production data** — a job can pass every integration test and still reveal
a discrepancy during parallel-run if the on-prem job's actual behavior
differs subtly from its documented/assumed behavior.

## Common Mistakes

- Treating integration tests as redundant with parallel-run validation and
  skipping one or the other — they catch different classes of problems and
  both are required.
- Running integration tests against shared, mutable `qa` test data that
  other tests or engineers also modify — this produces flaky,
  hard-to-reproduce failures. Use isolated, per-test-run data (a unique
  GCS prefix/BigQuery dataset per test run) instead.

## Production Notes

For Tier 1 jobs, integration test data should include at least one
realistic **peak-volume-shaped** test case (not just a small happy-path
sample) to catch any obvious performance cliff before the job reaches
[`17-performance/`](../17-performance/README.md) tuning and
[`21-cutover/`](../21-cutover/README.md).
