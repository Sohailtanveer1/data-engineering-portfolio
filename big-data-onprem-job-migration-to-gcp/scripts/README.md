# scripts — Operational Scripts

## Purpose

Reusable, executable scripts referenced throughout this repository's
phase documentation — rather than describing a script's logic in prose
only, the actual implementation lives here so it can be copied directly
into the platform's repositories and run.

## Owner

Platform Engineering.

## Scripts

| Script | Referenced From | Purpose |
|---|---|---|
| [`validate_storage_migration.py`](validate_storage_migration.py) | [`05-storage-migration/05-checksum-and-validation.md`](../05-storage-migration/05-checksum-and-validation.md) | File count/size/checksum comparison between HDFS source and GCS target |
| [`reconcile_table.py`](reconcile_table.py) | [`06-data-migration/07-data-reconciliation-framework.md`](../06-data-migration/07-data-reconciliation-framework.md), [`16-data-validation/01-validation-framework-architecture.md`](../16-data-validation/01-validation-framework-architecture.md) | Config-driven table-level reconciliation (counts, aggregates, nulls, duplicates, business rules) |
| [`check_dag_best_practices.py`](check_dag_best_practices.py) | [`09-composer-migration/04-dag-best-practices.md`](../09-composer-migration/04-dag-best-practices.md), [`ci-cd/workflows/dag-sync.yml`](../ci-cd/workflows/dag-sync.yml) | Static analysis enforcing the DAG authoring standard |
| [`determine_version.py`](determine_version.py) | [`ci-cd/06-environment-promotion-and-release.md`](../ci-cd/06-environment-promotion-and-release.md), [`ci-cd/workflows/spark-job-ci.yml`](../ci-cd/workflows/spark-job-ci.yml) | Semantic version bump determination from Conventional Commits |

## Usage

Each script is standalone and documented via its own `--help` output and
module docstring. None require a live GCP connection to run their
`--help`/dry-run mode, so they can be inspected and tested locally before
being pointed at a real environment.

## Conventions

Every script in this folder follows the same conventions as job code
elsewhere in this repository (per
[`07-spark-migration/08-oop-design-patterns.md`](../07-spark-migration/08-oop-design-patterns.md)):
no hardcoded values, structured output, explicit exit codes (0 = success,
non-zero = failure), and no destructive action taken without an explicit
`--apply`/`--confirm` flag where relevant.
