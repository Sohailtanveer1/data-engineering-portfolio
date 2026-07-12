# sample-config — Sample Configuration Files

## Purpose

Working example configuration files referenced throughout this
repository's documentation — the actual YAML/JSON, not just a description
of its shape.

## Owner

Platform Engineering.

## Files

| File | Referenced From |
|---|---|
| [`pricing-job-config/dev.yaml`](pricing-job-config/dev.yaml), [`qa.yaml`](pricing-job-config/qa.yaml), [`stage.yaml`](pricing-job-config/stage.yaml), [`prod.yaml`](pricing-job-config/prod.yaml) | [`07-spark-migration/05-configuration-management-and-secrets.md`](../07-spark-migration/05-configuration-management-and-secrets.md) — the `ConfigLoader` input per environment |
| [`validation-config-example.yaml`](validation-config-example.yaml) | [`16-data-validation/01-validation-framework-architecture.md`](../16-data-validation/01-validation-framework-architecture.md) — a real, complete validation engine config |
| [`dataproc-cluster-config-example.json`](dataproc-cluster-config-example.json) | [`12-cluster-design/`](../12-cluster-design/README.md) — the raw Dataproc cluster config shape underlying the Terraform module in [`terraform/modules/dataproc-cluster/`](../terraform/modules/dataproc-cluster) |

These files are meant to be copied and adapted per job/environment, not
used verbatim — every placeholder value (`<company>`, `<project-id>`)
must be replaced with real values before use.
