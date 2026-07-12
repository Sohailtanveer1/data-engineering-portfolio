# terraform — Reusable Terraform Modules

## Purpose

The actual, reusable Terraform module library implementing the strategy
and standards defined in
[`13-infrastructure/`](../13-infrastructure/README.md) — the standards
folder says *how* Terraform is organized and governed; this folder is
*what* actually gets applied.

## Owner

Cloud/DevOps, per
[`13-infrastructure/README.md`](../13-infrastructure/README.md).

## How this folder is structured

Per
[`13-infrastructure/01-terraform-folder-structure.md`](../13-infrastructure/01-terraform-folder-structure.md):

```
terraform/
├── modules/                  Reusable, environment-agnostic modules
│   ├── gcs-bucket/            Storage bucket with lifecycle, CMEK, naming validation
│   ├── iam-service-account/   Service account with scoped role/bucket bindings
│   ├── kms-keyring/           KMS key ring and key with rotation policy
│   └── dataproc-cluster/      Ephemeral-pattern Dataproc cluster configuration
└── environments/             Per-environment composition (dev shown as example)
    └── dev/
        └── main.tf            Example composing the modules above for the pricing domain
```

This is a representative subset of the full module catalog described in
[`13-infrastructure/01-terraform-folder-structure.md`](../13-infrastructure/01-terraform-folder-structure.md)
(which also lists `dataproc-metastore`, `composer-environment`,
`vpc-network`, and `bigquery-dataset` modules) — built out here to
demonstrate the pattern; the remaining modules follow the identical
internal structure (`main.tf`, `variables.tf`, `outputs.tf`) and naming/
validation conventions shown in these four.

## Module conventions

Every module in this folder:

- Takes **no environment-specific hardcoded values** — everything is a
  variable, per
  [`13-infrastructure/01-terraform-folder-structure.md`](../13-infrastructure/01-terraform-folder-structure.md).
- Enforces naming convention via variable validation blocks, per
  [`13-infrastructure/03-naming-and-tagging-standards.md`](../13-infrastructure/03-naming-and-tagging-standards.md).
- Applies the mandatory label set (`managed_by`, `environment`,
  `data_domain`, `criticality_tier`, `cost_center`) to every resource that
  supports labels.

## Usage

See
[`13-infrastructure/04-module-usage-guide.md`](../13-infrastructure/04-module-usage-guide.md)
for the full worked example, and
[`environments/dev/main.tf`](environments/dev/main.tf) in this folder for
a runnable composition of these modules.
