# Working CI/CD Pipeline Configurations

**Purpose:** Executable GitHub Actions workflow files implementing the
pipelines described in this folder's documentation. Copy these into a
repository's `.github/workflows/` directory as the starting point.

## Files

| File | Implements |
|---|---|
| [`spark-job-ci.yml`](spark-job-ci.yml) | [`../03-spark-job-pipeline.md`](../03-spark-job-pipeline.md) — lint, test, package, publish a Spark job |
| [`terraform-ci.yml`](terraform-ci.yml) | [`../04-terraform-pipeline.md`](../04-terraform-pipeline.md) — validate, plan, apply |
| [`dag-sync.yml`](dag-sync.yml) | [`../05-dag-deployment-pipeline.md`](../05-dag-deployment-pipeline.md) — validate and sync Composer DAGs |

## Placeholders to replace

Every workflow file uses `${{ vars.* }}` and `${{ secrets.* }}` references
that must be configured in the actual GitHub repository's environment
settings before use — most notably `WORKLOAD_IDENTITY_PROVIDER` and
`SERVICE_ACCOUNT_EMAIL`, per
[`../02-pipeline-architecture.md`](../02-pipeline-architecture.md)
Workload Identity Federation setup.
