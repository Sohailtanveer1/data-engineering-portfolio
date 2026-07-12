# 16 — Data Validation

## Purpose

Build the **automated, reusable validation framework** applied
continuously — during parallel-run, at cutover, and in ongoing production
— across every migrated dataset. This generalizes the migration-time,
per-load checks already defined in
[`05-storage-migration/05-checksum-and-validation.md`](../05-storage-migration/05-checksum-and-validation.md)
(byte-level) and
[`06-data-migration/07-data-reconciliation-framework.md`](../06-data-migration/07-data-reconciliation-framework.md)
(logical, migration-time) into a standing capability that keeps running
after those one-time gates are passed — because a job that validated
correctly on day one can still drift on day fifty due to a code change,
an upstream schema shift, or an edge case the original validation missed.

## Owner

**Data Engineering**, integrated with
[`18-monitoring/`](../18-monitoring/README.md) for continuous production
operation.

## Inputs

- Validation logic already built in
  [`05-storage-migration/05-checksum-and-validation.md`](../05-storage-migration/05-checksum-and-validation.md)
  and
  [`06-data-migration/07-data-reconciliation-framework.md`](../06-data-migration/07-data-reconciliation-framework.md)
  — generalized here into a reusable framework, not rebuilt from scratch.
- Business validation rules confirmed during
  [`01-discovery/questions/05-business.md`](../01-discovery/questions/05-business.md).

## Outputs

- A reusable, automated validation framework applicable to any table/job.
- Standing reconciliation reports for every Tier 1/2 dataset, running
  continuously in production.

## Prerequisites

[`06-data-migration/`](../06-data-migration/README.md) providing the
migration-time validation baseline this framework generalizes from.

## Deliverables

1. Validation framework architecture (how it runs, how it's triggered).
2. Count and checksum validation (generalized, reusable).
3. Aggregation validation.
4. Business rule validation.
5. Duplicate and null detection.
6. Reconciliation reporting.
7. Continuous validation in production (post-cutover).

## Risks

A validation framework that only runs once, at migration time, misses
drift introduced by any subsequent code or data change — this folder
exists specifically to prevent that gap.

## Rollback

N/A — validation is read-only; a validation failure triggers investigation
and potentially a job-level rollback per
[`14-job-migration/06-rollback-procedures.md`](../14-job-migration/06-rollback-procedures.md),
but the validation process itself has nothing to roll back.

## Validation

The framework itself must be validated against known-good and
deliberately-corrupted test data to confirm it actually catches the
discrepancies it's designed to catch — an untested validation framework is
a false safety net.

## Best Practices

Build the framework once, generically, parameterized per table/job — not
a bespoke validation script per dataset, mirroring the reusability
principle applied throughout
[`07-spark-migration/`](../07-spark-migration/README.md).

## Lessons Learned

Validation that only runs during the migration window and is then
switched off is a common gap — data drift and silent corruption are
ongoing risks, not just a migration-day risk.

## Common Mistakes

- Treating this folder as redundant with
  [`06-data-migration/07-data-reconciliation-framework.md`](../06-data-migration/07-data-reconciliation-framework.md)
  and skipping it — that framework is scoped to the one-time migration
  load; this one is the generalized, continuously-running capability.
- Building validation checks that alert on every minor variance, causing
  alert fatigue that leads to real issues being ignored.

## Production Notes

For Tier 1 datasets, continuous validation must run at a frequency
matched to the job's own schedule (e.g., after every `fraud_score_hourly`
run, not just daily) — see
[`07-continuous-validation-in-production.md`](07-continuous-validation-in-production.md).

---

## Folder structure

```
16-data-validation/
├── README.md                                          This file
├── 01-validation-framework-architecture.md             How the framework runs, reusably
├── 02-count-and-checksum-validation.md                 Generalized count/checksum checks
├── 03-aggregation-validation.md                        Sum/avg/min/max validation
├── 04-business-rule-validation.md                      Encoding confirmed business rules as checks
├── 05-duplicate-and-null-detection.md                  Data quality checks
├── 06-reconciliation-reporting.md                       Report format and distribution
└── 07-continuous-validation-in-production.md            Post-cutover, ongoing operation
```
