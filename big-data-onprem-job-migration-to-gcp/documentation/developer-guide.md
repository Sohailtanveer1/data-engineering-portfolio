# Developer Guide

**Purpose:** The single starting point for an engineer about to migrate a
Spark job — pointing to the relevant phase documents in the right order,
rather than requiring them to discover the structure independently.
**Audience:** Data/Platform Engineers.

---

## Before you start

1. Read [`07-spark-migration/README.md`](../07-spark-migration/README.md)
   in full — it explains the philosophy (re-engineer, not just
   re-platform) that shapes everything below.
2. Read your job's dependency card, per
   [`02-dependency-analysis/templates/02-job-dependency-card-template.md`](../02-dependency-analysis/templates/02-job-dependency-card-template.md)
   — if one doesn't exist yet for your job, that's the first thing to
   build.
3. Confirm the shared library (`data-platform-spark-common`) version
   you'll build against — check
   [`07-spark-migration/04-packaging-and-dependency-management.md`](../07-spark-migration/04-packaging-and-dependency-management.md)
   for the current stable version.

## Your job repository, step by step

1. **Scaffold** the repository per
   [`07-spark-migration/01-repository-restructuring.md`](../07-spark-migration/01-repository-restructuring.md).
2. **Use the shared patterns**, don't reinvent them — copy from
   [`07-spark-migration/examples/`](../07-spark-migration/examples/README.md)
   as your starting point (`SparkSessionFactory`, `ConfigLoader`,
   `PipelineBuilder`, `retryable`).
3. **Externalize every hardcoded value** you find during migration, per
   [`07-spark-migration/05-configuration-management-and-secrets.md`](../07-spark-migration/05-configuration-management-and-secrets.md).
4. **Make it idempotent** — verify explicitly per
   [`07-spark-migration/07-idempotency-design.md`](../07-spark-migration/07-idempotency-design.md).
5. **Write tests** — unit tests per
   [`07-spark-migration/09-unit-testing-strategy.md`](../07-spark-migration/09-unit-testing-strategy.md)
   as you go, not after; integration tests per
   [`07-spark-migration/10-integration-testing-strategy.md`](../07-spark-migration/10-integration-testing-strategy.md)
   once the job is functionally complete.
6. **Build the DAG** per
   [`09-composer-migration/`](../09-composer-migration/README.md) —
   check whether your job fits the dynamic DAG generation pattern
   ([`09-composer-migration/03-dynamic-dag-generation.md`](../09-composer-migration/03-dynamic-dag-generation.md))
   before hand-writing a DAG file.
7. **Open a PR** — per
   [`ci-cd/01-repository-and-branching-strategy.md`](../ci-cd/01-repository-and-branching-strategy.md).
   The pipeline (per
   [`ci-cd/03-spark-job-pipeline.md`](../ci-cd/03-spark-job-pipeline.md))
   runs lint, tests, and packaging automatically.

## Common questions

| Question | Answer |
|---|---|
| "Where do I put business logic vs. orchestration?" | Business logic in `transformations/`, orchestration wiring in `main.py` via `PipelineBuilder` — see [`07-spark-migration/01-repository-restructuring.md`](../07-spark-migration/01-repository-restructuring.md) |
| "How do I know if my job should be ephemeral or persistent?" | [`04-target-architecture/03-compute-architecture.md`](../04-target-architecture/03-compute-architecture.md) decision framework |
| "How do I get a new secret into Secret Manager?" | [`10-security/03-secret-manager-design.md`](../10-security/03-secret-manager-design.md) — request via Security Engineering |
| "What tier is my job, and does that change what I need to do?" | Check [`01-discovery/inventories/02-business-critical-jobs.md`](../01-discovery/inventories/02-business-critical-jobs.md); tier changes test coverage, validation rigor, and wave placement per [`14-job-migration/01-priority-matrix.md`](../14-job-migration/01-priority-matrix.md) |

## Getting help

Escalation path per
[`00-project-overview/03-raci-matrix.md`](../00-project-overview/03-raci-matrix.md).
For shared library questions specifically, contact the shared-library
owner role referenced in
[`07-spark-migration/README.md`](../07-spark-migration/README.md).
