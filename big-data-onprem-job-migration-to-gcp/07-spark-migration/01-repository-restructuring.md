# Repository Restructuring & Code Cleanup

**Purpose:** Establish a standard repository structure applied to every
migrated Spark job, replacing inconsistent on-prem repository layouts
(where they exist at all — some jobs may have grown organically with no
formal structure) with a predictable, testable, CI/CD-friendly layout.
**Owner:** Platform Engineering.

---

## Reference project structure (per job repository)

```
pricing-nightly-batch/
├── pyproject.toml                 Build/dependency definition (Python) — or pom.xml/build.sbt for Scala
├── README.md                      Job-specific README (purpose, owner, SLA, dependencies)
├── src/
│   └── pricing_nightly_batch/
│       ├── __init__.py
│       ├── main.py                Entry point — thin, orchestrates the job, no business logic
│       ├── config.py               Job-specific config schema (extends shared ConfigLoader)
│       ├── transformations/       Business logic, organized by transformation step
│       │   ├── __init__.py
│       │   ├── price_calculation.py
│       │   └── zone_mapping.py
│       └── io/                     Read/write logic, using shared I/O utilities
│           ├── __init__.py
│           ├── readers.py
│           └── writers.py
├── tests/
│   ├── unit/                       Fast, no-Spark-cluster-needed tests
│   │   ├── test_price_calculation.py
│   │   └── test_zone_mapping.py
│   └── integration/                Tests requiring a local/test Spark session
│       └── test_pricing_pipeline_e2e.py
├── config/
│   ├── dev.yaml
│   ├── qa.yaml
│   ├── stage.yaml
│   └── prod.yaml                   No secrets — see 05-configuration-management-and-secrets.md
└── dag/
    └── pricing_nightly_batch_dag.py  Composer DAG definition — see 09-composer-migration/
```

## Shared library repository structure (separate repo)

```
data-platform-spark-common/
├── pyproject.toml
├── src/
│   └── dp_spark_common/
│       ├── session/
│       │   └── factory.py          SparkSessionFactory — see 08-oop-design-patterns.md
│       ├── config/
│       │   └── loader.py           ConfigLoader — see 08-oop-design-patterns.md
│       ├── io/
│       │   ├── gcs.py               Standardized GCS read/write helpers
│       │   └── bigquery.py          Standardized BigQuery read/write helpers
│       ├── logging/
│       │   └── structured_logger.py
│       ├── retry/
│       │   └── decorator.py         Retry logic — see 06-logging-and-error-handling.md
│       └── secrets/
│           └── secret_manager_client.py
└── tests/
    ├── unit/
    └── integration/
```

Every job repository declares a versioned dependency on
`data-platform-spark-common` (see
[`04-packaging-and-dependency-management.md`](04-packaging-and-dependency-management.md))
rather than duplicating this logic per job.

## Code cleanup standard applied during migration

Every job migrated under this standard must, at minimum:

1. **Remove all hardcoded values** — paths, hostnames, credentials,
   cluster names — replaced by the configuration pattern in
   [`05-configuration-management-and-secrets.md`](05-configuration-management-and-secrets.md).
2. **Separate business logic from I/O and orchestration** — transformation
   logic in `transformations/` must be independently unit-testable without
   a live Spark cluster or real GCS/BigQuery connection wherever feasible
   (pure functions/DataFrame transformations operating on already-loaded
   DataFrames).
3. **Remove dead code** — commented-out blocks, unused imports, and
   abandoned feature-flagged branches identified during
   [`02-dependency-analysis/methodology/01-spark-job-dependencies.md`](../02-dependency-analysis/methodology/01-spark-job-dependencies.md)
   analysis — but only after confirming with the job owner (per
   [`01-discovery/questions/06-developers.md`](../01-discovery/questions/06-developers.md))
   that it's genuinely unused, not a rarely-exercised fallback path.
4. **Add type hints** (Python) or maintain strict typing (Scala) per the
   coding standard in the root
   [`README.md`](../README.md#coding--documentation-standards).

## What NOT to change during this pass

Per the charter's scope boundary
([`00-project-overview/02-migration-charter.md`](../00-project-overview/02-migration-charter.md)),
this phase does **not** redesign business logic or add new features — a
job's actual transformation behavior (the numbers it computes, the
business rules it applies) must remain identical unless a specific,
separately-reviewed bug fix is explicitly agreed with the job owner and
Business Owner, and documented as such.

## Common Mistakes

- Restructuring a job's code and its business logic in the same change,
  making it impossible to isolate whether a validation discrepancy (per
  [`16-data-validation/`](../16-data-validation/README.md)) came from a
  structural refactor or an actual logic change.
- Copying business logic directly into the shared library "for
  convenience" — the shared library should contain only genuinely
  cross-job, generic utilities (session creation, config loading, I/O,
  logging, retry), never job-specific business rules.

## Production Notes

For Tier 1 jobs, perform the restructuring and the parallel-run validation
as two clearly separated, sequential steps with a passing validation
result required before the job proceeds toward its cutover wave — don't
compress structural cleanup and final validation into a single rushed
pass.
