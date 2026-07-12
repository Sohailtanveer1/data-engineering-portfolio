# CI/CD Pipeline

## Purpose

Provide the complete, automated build/test/deploy pipeline for every kind
of change in this platform — Spark job code, the shared library,
Terraform infrastructure, and Composer DAGs — enforcing every quality gate
established throughout this repository (testing, validation, naming
standards, environment promotion) automatically rather than relying on
manual discipline.

## Owner

**Cloud/DevOps**, with pipeline stages reviewed by Platform Engineering
(Spark/DAG pipelines) and Security Engineering (Terraform pipeline,
given its production infrastructure impact).

## Inputs

- Testing standards from
  [`07-spark-migration/09-unit-testing-strategy.md`](../07-spark-migration/09-unit-testing-strategy.md)
  and
  [`07-spark-migration/10-integration-testing-strategy.md`](../07-spark-migration/10-integration-testing-strategy.md).
- Terraform structure from
  [`13-infrastructure/`](../13-infrastructure/README.md).
- Environment promotion model from
  [`13-infrastructure/05-environment-promotion.md`](../13-infrastructure/05-environment-promotion.md).

## Outputs

- Fully automated pipelines for Spark job packages, the shared library,
  Terraform, and Composer DAGs.
- Enforced quality gates: tests, formatting, linting, security scanning.
- A working release/versioning/rollback mechanism.

## Prerequisites

[`13-infrastructure/`](../13-infrastructure/README.md) providing the
Artifact Registry and environment structure these pipelines deploy into.

## Deliverables

1. Repository and branching strategy.
2. Pipeline architecture (tool choice, stage design).
3. Spark job pipeline (build, test, package, publish).
4. Terraform pipeline (validate, plan, apply).
5. DAG deployment pipeline.
6. Environment promotion and release strategy.
7. Working pipeline configuration files in
   [`workflows/`](workflows/).

## Risks

A pipeline that's too permissive (weak gates) lets defects reach
production; a pipeline that's too rigid (excessive manual approval steps)
slows the team down enough that people route around it — this folder
aims for the calibrated middle documented throughout.

## Rollback

Pipeline configuration itself is version-controlled — a bad pipeline
change is reverted like any other code change. Deployment rollback
(rolling back a bad artifact) is addressed in
[`06-environment-promotion-and-release.md`](06-environment-promotion-and-release.md).

## Validation

The pipeline itself is validated by deliberately introducing a failing
test/lint/validation check and confirming the pipeline correctly blocks
the change — pipelines that are never tested against a failure case are
of unknown reliability.

## Best Practices

Every quality gate enforced in code review guidance elsewhere in this
repository (e.g.,
[`09-composer-migration/04-dag-best-practices.md`](../09-composer-migration/04-dag-best-practices.md)
checklist) should also be enforced automatically here — a checklist a
human might skip under pressure is far less reliable than an automated
gate.

## Lessons Learned

Manual deployment processes that "work fine" during a migration's early,
low-volume phase reliably become a bottleneck and error source once wave
execution reaches full velocity across many jobs simultaneously.

## Common Mistakes

- Building pipelines only for Spark jobs and treating Terraform/DAG
  deployment as separately, informally managed.
- Allowing `prod` deployment approval to become a rubber-stamp click
  instead of genuine review.

## Production Notes

Every `prod` pipeline run (Terraform apply, job package publish, DAG sync)
is logged with full audit detail — who approved, what changed — feeding
both [`10-security/05-audit-logging.md`](../10-security/05-audit-logging.md)
and [`logs/`](../logs/README.md).

---

## Folder structure

```
ci-cd/
├── README.md                                       This file
├── 01-repository-and-branching-strategy.md          GitFlow, branching, PR/code review
├── 02-pipeline-architecture.md                      Tool choice, stage design
├── 03-spark-job-pipeline.md                          Build, test, package, publish
├── 04-terraform-pipeline.md                          Validate, fmt, lint, plan, apply
├── 05-dag-deployment-pipeline.md                     Composer DAG sync pipeline
├── 06-environment-promotion-and-release.md           Promotion, tagging, versioning, rollback
└── workflows/                                        Working pipeline configuration
    ├── README.md
    ├── spark-job-ci.yml
    ├── terraform-ci.yml
    └── dag-sync.yml
```
