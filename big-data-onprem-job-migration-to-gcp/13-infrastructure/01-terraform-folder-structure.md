# Terraform Folder Structure Standard

**Purpose:** Define where Terraform code lives and how it's organized,
separating reusable modules from per-environment configuration.
**Owner:** Cloud/DevOps.

---

## Repository layout

```
terraform/                              Root-level, reusable module library (see terraform/README.md)
├── modules/
│   ├── gcs-bucket/
│   ├── dataproc-cluster/
│   ├── dataproc-metastore/
│   ├── composer-environment/
│   ├── iam-service-account/
│   ├── kms-keyring/
│   ├── vpc-network/
│   └── bigquery-dataset/
└── environments/                       Per-environment configuration, composing modules
    ├── dev/
    │   ├── main.tf                     Module calls with dev-specific variables
    │   ├── variables.tf
    │   ├── terraform.tfvars
    │   └── backend.tf                  Points at this environment's remote state
    ├── qa/
    ├── stage/
    └── prod/
```

## Separation principle: modules vs. environments

- **`modules/`** contain **no environment-specific values** — every
  project ID, bucket name, and region is a variable, never hardcoded. A
  module is reusable precisely because it doesn't know which environment
  it's being applied to.
- **`environments/<env>/`** contain the actual environment-specific
  values (via `terraform.tfvars`) and the specific combination of module
  calls that make up that environment — this is where `dev` and `prod`
  genuinely differ (e.g., `prod` uses HA mode for persistent clusters per
  [`12-cluster-design/05-high-availability-design.md`](../12-cluster-design/05-high-availability-design.md),
  `dev` doesn't).

## Module internal structure

Every module in `terraform/modules/` follows the same internal layout:

```
modules/dataproc-cluster/
├── main.tf          Resource definitions
├── variables.tf      Input variable declarations, with descriptions and types
├── outputs.tf         Output value declarations
├── versions.tf        Required provider versions
└── README.md          Usage documentation, example invocation
```

## Why this structure, not a single flat set of `.tf` files

A flat structure (all resources in one set of files, environment
differences handled via `count`/`if` conditionals) becomes unreadable and
error-prone at the scale of this platform (multiple environments, many
job families, many data domains). The module/environment separation keeps
each piece small, independently reviewable, and testable in isolation —
directly mirroring the same "small, composable, testable units" principle
applied to Spark job code in
[`07-spark-migration/01-repository-restructuring.md`](../07-spark-migration/01-repository-restructuring.md).

## Common Mistakes

- Hardcoding an environment-specific value inside a module "just this
  once" — this breaks the module's reusability guarantee and creates a
  hidden environment dependency that's easy to miss in review.
- Duplicating near-identical module code across environments instead of
  parameterizing a single shared module — this is the infrastructure
  equivalent of the code-duplication anti-pattern flagged throughout
  [`07-spark-migration/`](../07-spark-migration/README.md).

## Production Notes

Every module intended for `prod` use must have a working, tested
invocation in at least `dev` and `qa` before being referenced from the
`prod` environment configuration — see
[`05-environment-promotion.md`](05-environment-promotion.md).
