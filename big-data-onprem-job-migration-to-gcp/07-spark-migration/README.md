# 07 — Spark Code Migration

## Purpose

This is the largest and highest-risk technical phase in the program. Every
Spark job identified in
[`01-discovery/inventories/08-spark-inventory.md`](../01-discovery/inventories/08-spark-inventory.md)
must be re-platformed to run on Dataproc — not as a mechanical port, but as
a deliberate rebuild that fixes the technical debt surfaced in
[`03-current-environment/09-pain-points-and-bottlenecks.md`](../03-current-environment/09-pain-points-and-bottlenecks.md)
(hardcoded values, client-mode edge-node dependencies, missing idempotency,
inconsistent submission patterns) while preserving exact business logic
behavior.

## Owner

**Data/Platform Engineering**, with a dedicated **shared-library owner**
role responsible for the common utilities every job depends on (see
[`08-oop-design-patterns.md`](08-oop-design-patterns.md)).

## Inputs

- Spark inventory and per-job dependency cards from
  [`01-discovery/inventories/08-spark-inventory.md`](../01-discovery/inventories/08-spark-inventory.md)
  and
  [`02-dependency-analysis/templates/02-job-dependency-card-template.md`](../02-dependency-analysis/templates/02-job-dependency-card-template.md).
- Target compute architecture from
  [`04-target-architecture/03-compute-architecture.md`](../04-target-architecture/03-compute-architecture.md).
- Migrated, validated data from
  [`05-storage-migration/`](../05-storage-migration/README.md) and
  [`06-data-migration/`](../06-data-migration/README.md).

## Outputs

- A shared internal Spark library, rebuilt once and reused by every job,
  covering session creation, configuration loading, logging, retry, and
  I/O patterns.
- Every in-scope job re-platformed, packaged, and running on Dataproc via
  a standardized submission pattern.
- A test suite (unit + integration) for the shared library and for every
  Tier 1/2 job.

## Prerequisites

[`04-target-architecture/`](../04-target-architecture/README.md) gated;
[`12-cluster-design/`](../12-cluster-design/README.md) cluster patterns
defined (this phase builds against that design, though the two can proceed
in parallel with close coordination); relevant data domains migrated per
[`05-storage-migration/`](../05-storage-migration/README.md) so migrated
jobs have real data to validate against.

## Deliverables

1. Repository restructuring standard and reference project structure.
2. Spark/Scala/Python version migration plan, including deprecated API
   remediation.
3. Standardized Dataproc job submission pattern (cluster modes,
   autoscaling, init actions).
4. Packaging and dependency management standard (build tooling, Artifact
   Registry).
5. Configuration management and secrets externalization pattern.
6. Structured logging and error-handling/retry-logic standard.
7. Idempotency design pattern and per-job verification requirement.
8. OOP design patterns (factory, builder, configuration pattern) with
   working code examples in [`examples/`](examples/).
9. Unit and integration testing strategy.

## Risks

- **Rebuilding the shared library incorrectly** has the widest blast
  radius of any risk in this phase — every job depends on it. Mitigated by
  the shared-library-first build order (see
  [`02-dependency-analysis/templates/03-dependency-matrix-inventory-template.md`](../02-dependency-analysis/templates/03-dependency-matrix-inventory-template.md)
  reuse ranking) and mandatory comprehensive test coverage before any job
  built on it proceeds.
- **Silently changing business logic while "cleaning up" code** — this
  phase explicitly permits technical debt cleanup (hardcoded values,
  submission pattern, error handling) but must preserve exact business
  logic behavior; any intentional logic change must be flagged and
  reviewed separately, not bundled invisibly into the migration.

## Rollback

Per job: if a migrated job fails validation, the on-prem job continues to
run unaffected (per constraint C7) — see
[`14-job-migration/`](../14-job-migration/README.md) rollback guidance.
Per shared library: versioned releases (see
[`04-packaging-and-dependency-management.md`](04-packaging-and-dependency-management.md))
allow any job to pin to a known-good prior version if a new library release
introduces a regression.

## Validation

A job is not considered migrated until it passes: unit tests, integration
tests against real (validated) migrated data, a parallel-run comparison
against its on-prem output per
[`16-data-validation/`](../16-data-validation/README.md), and explicit
idempotency verification (re-run produces identical output).

## Best Practices

Migrate and thoroughly test the shared library and one pilot job end-to-end
before parallelizing across many jobs — this phase's cost is dominated by
the shared library and pattern-setting work, not by the marginal cost of
each additional job once the pattern is proven.

## Lessons Learned

Jobs migrated under time pressure by copy-pasting the old logic into a new
submission wrapper without addressing the underlying technical debt
(hardcoded paths, non-idempotent writes) simply relocate the current
platform's problems onto more expensive cloud infrastructure — the
business case in
[`00-project-overview/01-executive-summary.md`](../00-project-overview/01-executive-summary.md)
depends on this phase doing real re-engineering, not just re-platforming.

## Common Mistakes

- Treating every job as a one-off migration instead of maximizing reuse of
  the shared library and standardized patterns — this multiplies effort
  and inconsistency across hundreds of jobs.
- Skipping unit/integration test creation for jobs that "already work,"
  under time pressure — see
  [`09-unit-testing-strategy.md`](09-unit-testing-strategy.md) for why
  this is a hard requirement, not a nice-to-have, especially for jobs with
  no prior test coverage per
  [`01-discovery/questions/06-developers.md`](../01-discovery/questions/06-developers.md)
  Q9.

## Production Notes

Tier 1 jobs (pricing, fraud, inventory, finance) should be migrated only
after the shared library and submission pattern have been proven on
several Tier 2/3 jobs first — Tier 1 jobs should never be the first real
test of a new pattern.

---

## Folder structure

```
07-spark-migration/
├── README.md                                        This file
├── 01-repository-restructuring.md                    Project structure, code cleanup standard
├── 02-spark-version-and-api-migration.md              Version upgrade plan, deprecated API remediation
├── 03-dataproc-submission-patterns.md                 Cluster modes, autoscaling, init actions, submission
├── 04-packaging-and-dependency-management.md          Build tooling, Artifact Registry, versioning
├── 05-configuration-management-and-secrets.md         Config externalization, Secret Manager pattern
├── 06-logging-and-error-handling.md                   Structured logging, error handling, retry logic
├── 07-idempotency-design.md                            Idempotency patterns and verification
├── 08-oop-design-patterns.md                           Factory, builder, configuration patterns
├── 09-unit-testing-strategy.md                         Unit testing standard
├── 10-integration-testing-strategy.md                  Integration testing standard
└── examples/                                            Working, executable reference code
    ├── README.md
    ├── config_loader.py
    ├── spark_session_factory.py
    ├── job_builder.py
    ├── retry_decorator.py
    ├── example_pricing_job.py
    └── test_example_pricing_job.py
```
