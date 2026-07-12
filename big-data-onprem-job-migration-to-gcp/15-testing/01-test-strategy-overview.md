# Test Strategy Overview

**Purpose:** A single reference matrix of every test category used across
this migration, its purpose, ownership, and where it's detailed.
**Owner:** QA / Test Engineering.

---

## Test type matrix

| Test Type | Purpose | Owner | Detailed In | Automated? |
|---|---|---|---|---|
| Unit | Transformation logic correctness, no cluster/network needed | Data/Platform Engineering | [`07-spark-migration/09-unit-testing-strategy.md`](../07-spark-migration/09-unit-testing-strategy.md) | Yes — every CI run |
| Integration | Full job pipeline against real (test) GCS/BigQuery | Data/Platform Engineering + QA | [`07-spark-migration/10-integration-testing-strategy.md`](../07-spark-migration/10-integration-testing-strategy.md) | Yes — on merge to release branch |
| Regression | Confirm a change doesn't break previously-working behavior | QA | [`02-regression-testing.md`](02-regression-testing.md) | Yes |
| Smoke | Fast, shallow sanity check post-deployment | Platform Engineering | [`03-smoke-testing.md`](03-smoke-testing.md) | Yes — post every deployment |
| End-to-end | Full DAG execution, Composer through to final output | QA | [`04-end-to-end-testing.md`](04-end-to-end-testing.md) | Yes, in qa/stage |
| Performance | Job meets SLA under representative/peak load | Platform Engineering | [`08-performance-testing-overview.md`](08-performance-testing-overview.md), [`17-performance/`](../17-performance/README.md) | Partially — load generation automated, analysis manual |
| Recovery | System recovers correctly from a failure | Platform Engineering | [`05-recovery-testing.md`](05-recovery-testing.md) | Partially |
| Chaos | Deliberately injected failures reveal resilience gaps | Platform Engineering | [`06-chaos-testing.md`](06-chaos-testing.md) | Partially |
| Negative | Invalid/malformed/missing input handled correctly | QA | [`07-negative-testing.md`](07-negative-testing.md) | Yes |

## Test environment mapping

| Test Type | Runs In |
|---|---|
| Unit | Local / CI runner, no GCP environment needed |
| Integration | `qa` |
| Regression | `qa` |
| Smoke | Every environment, immediately post-deployment |
| End-to-end | `qa` / `stage` |
| Performance | `stage` (production-representative sizing) |
| Recovery / Chaos | `stage` (never `prod`, except for pre-approved, carefully scoped game days post-hypercare) |
| Negative | `qa` |

## Required test coverage by job tier

| Tier | Required Test Types |
|---|---|
| Tier 1 | All 9 types, full coverage, including chaos/recovery |
| Tier 2 | Unit, integration, regression, smoke, end-to-end, negative — performance/chaos/recovery recommended but not blocking |
| Tier 3 | Unit, integration, smoke — remaining types recommended, applied opportunistically |

## Common Mistakes

- Applying Tier 1 rigor uniformly to every job regardless of tier, making
  the testing burden unsustainable at scale — the tiered requirement table
  exists specifically to focus the heaviest testing investment where it
  matters most.
- Running chaos/recovery testing directly in `prod` outside a carefully
  planned, pre-approved game day — this is testing methodology, not an
  invitation to experiment on production.

## Production Notes

Review this test type matrix against actual results at the end of each
wave (per
[`14-job-migration/02-wave-planning.md`](../14-job-migration/02-wave-planning.md))
— if a test category consistently isn't catching real issues, or is
catching disproportionately many, adjust investment accordingly for
subsequent waves.
