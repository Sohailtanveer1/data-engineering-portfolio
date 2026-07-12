# 15 — Testing

## Purpose

Provide the full-platform test strategy — beyond the unit/integration
testing already defined per-job in
[`07-spark-migration/09-unit-testing-strategy.md`](../07-spark-migration/09-unit-testing-strategy.md)
and
[`07-spark-migration/10-integration-testing-strategy.md`](../07-spark-migration/10-integration-testing-strategy.md)
— covering regression, smoke, end-to-end (full DAG), recovery, chaos, and
negative testing, so every category the charter and industry practice
expect from a production migration is deliberately addressed, not
assumed covered by "we have some unit tests."

## Owner

**QA / Test Engineering**, with Platform Engineering support for
infrastructure-level tests (chaos, recovery).

## Inputs

- Migrated, unit/integration-tested job code from
  [`07-spark-migration/`](../07-spark-migration/README.md).
- Built DAGs from [`09-composer-migration/`](../09-composer-migration/README.md).
- Provisioned test environments from
  [`13-infrastructure/`](../13-infrastructure/README.md).

## Outputs

- A complete, automated test suite per test category, integrated with
  [`ci-cd/`](../ci-cd/README.md).
- Test results feeding
  [`14-job-migration/07-production-deployment-checklist.md`](../14-job-migration/07-production-deployment-checklist.md)
  gates.

## Prerequisites

[`07-spark-migration/`](../07-spark-migration/README.md) and
[`09-composer-migration/`](../09-composer-migration/README.md) providing
tested job code and DAGs to test at the platform level.

## Deliverables

1. Test strategy overview (test type matrix, ownership, tooling).
2. Regression testing approach.
3. Smoke testing approach.
4. End-to-end (full DAG) testing approach.
5. Recovery testing approach.
6. Chaos testing approach.
7. Negative testing approach.
8. Performance testing process (full tuning detail in
   [`17-performance/`](../17-performance/README.md)).

## Risks

Under-investing in chaos/recovery testing because "unit tests pass" is a
common gap — these test categories exist specifically to catch failure
modes unit/integration tests structurally cannot (infrastructure failure,
partial outages, unexpected input).

## Rollback

N/A — testing itself doesn't modify production; test findings drive
rollback decisions elsewhere (per
[`14-job-migration/06-rollback-procedures.md`](../14-job-migration/06-rollback-procedures.md)).

## Validation

Every Tier 1 job must pass every applicable test category in this folder
before proceeding to
[`20-uat/`](../20-uat/README.md) — no test category is optional for
Tier 1.

## Best Practices

Automate every test category possible and run it in
[`ci-cd/`](../ci-cd/README.md) on every relevant change — manual testing
doesn't scale across hundreds of jobs and doesn't provide the repeatable
regression protection automation does.

## Lessons Learned

Chaos testing (deliberately injecting failures) consistently surfaces
issues that no amount of "the happy path works" testing catches — this is
precisely why it's included despite being the least commonly implemented
test category in most migrations.

## Common Mistakes

- Treating "the job ran successfully once in qa" as equivalent to having
  a real test suite.
- Skipping negative/chaos testing for Tier 1 jobs specifically because
  they're "too important to risk breaking in testing" — this reasoning is
  backwards; Tier 1 jobs need this testing most, in a safe non-production
  environment, precisely because a real failure in production would be
  most costly.

## Production Notes

For every Tier 1 job, explicitly schedule chaos and recovery testing time
in the wave plan (per
[`14-job-migration/02-wave-planning.md`](../14-job-migration/02-wave-planning.md))
— don't treat it as optional buffer time that gets cut when the schedule
tightens.

---

## Folder structure

```
15-testing/
├── README.md                              This file
├── 01-test-strategy-overview.md            Full test type matrix, ownership, tooling
├── 02-regression-testing.md                Ensuring changes don't break existing behavior
├── 03-smoke-testing.md                     Fast post-deployment sanity checks
├── 04-end-to-end-testing.md                Full DAG-level (Composer → Dataproc → output)
├── 05-recovery-testing.md                  Failure and recovery validation
├── 06-chaos-testing.md                     Deliberate fault injection
├── 07-negative-testing.md                  Invalid/malformed input handling
└── 08-performance-testing-overview.md      Process and gates (detail in 17-performance/)
```

Note: unit and integration testing standards for individual Spark jobs are
defined in
[`07-spark-migration/09-unit-testing-strategy.md`](../07-spark-migration/09-unit-testing-strategy.md)
and
[`07-spark-migration/10-integration-testing-strategy.md`](../07-spark-migration/10-integration-testing-strategy.md)
respectively — not duplicated here.
