# 13 — Infrastructure as Code (Terraform)

## Purpose

Define the Terraform strategy for this migration program: folder
structure, backend/state management, naming/tagging standards, and
environment promotion — the operating discipline that turns every design
decision from `04-`, `10-`, `11-`, and `12-` into actually-provisioned,
version-controlled, reviewable infrastructure. Constraint C5
([`00-project-overview/06-assumptions-and-constraints.md`](../00-project-overview/06-assumptions-and-constraints.md))
mandates all infrastructure is provisioned via Terraform — no manual
ClickOps changes in any environment, especially `prod`.

The actual reusable Terraform **modules** (GCS, Dataproc, Composer, IAM,
network, KMS) live in the root [`terraform/`](../terraform/README.md)
folder; this folder is the strategy and standards layer that governs how
those modules are organized, versioned, and applied per environment.

## Owner

**Cloud/DevOps**, with every module reviewed by Platform Engineering and,
for security-relevant modules (IAM, KMS), Security Engineering.

## Inputs

- Every design document from
  [`04-target-architecture/`](../04-target-architecture/README.md),
  [`10-security/`](../10-security/README.md),
  [`11-network/`](../11-network/README.md), and
  [`12-cluster-design/`](../12-cluster-design/README.md).

## Outputs

- A Terraform folder structure and module library capable of provisioning
  every environment (dev/qa/stage/prod) from version-controlled
  configuration.
- A working remote state backend with locking.
- Environment promotion process (dev → qa → stage → prod) integrated with
  [`ci-cd/`](../ci-cd/README.md).

## Prerequisites

[`04-target-architecture/`](../04-target-architecture/README.md),
[`10-security/`](../10-security/README.md), and
[`11-network/`](../11-network/README.md) gated.

## Deliverables

1. Terraform folder structure standard.
2. Backend and remote state configuration.
3. Naming and tagging standards (Terraform-enforced).
4. Module usage guide.
5. Environment promotion process.
6. State management and locking procedure.
7. Execution checklist.

## Risks

- **State file corruption or loss** without proper backend/locking
  configuration — mitigated by
  [`02-backend-and-remote-state.md`](02-backend-and-remote-state.md).
- **Configuration drift** if any environment is ever modified outside
  Terraform — mitigated by the governance model in
  [`06-cluster-policies-and-governance.md`](../12-cluster-design/06-cluster-policies-and-governance.md)
  and periodic drift-detection in [`ci-cd/`](../ci-cd/README.md).

## Rollback

Terraform's own state history and version control provide the rollback
mechanism — reverting to a prior commit and re-applying restores prior
infrastructure state (with the caveat that some resources, like a deleted
GCS bucket with versioning disabled, are not perfectly reversible — see
[`02-backend-and-remote-state.md`](02-backend-and-remote-state.md) for
state-specific rollback guidance).

## Validation

Every module must pass `terraform validate`, `terraform fmt -check`, and a
`terraform plan` review (no unexpected changes) in CI before being applied
to any environment, per [`ci-cd/`](../ci-cd/README.md).

## Best Practices

Build and test every module against `dev` first, promote to `qa`/`stage`,
and only then apply to `prod` — never apply an unproven module
configuration directly to production.

## Lessons Learned

Terraform modules built too generically ("one module to rule them all")
become harder to reason about than a slightly larger number of purpose-
specific modules with clear, narrow responsibility — see the module
design principle in
[`terraform/README.md`](../terraform/README.md).

## Common Mistakes

- Manually editing a resource in the GCP Console "just this once" and
  letting Terraform state drift out of sync — always change through
  Terraform, even for urgent fixes (use a fast-tracked PR process instead
  of bypassing IaC).
- Storing Terraform state locally or in a non-versioned, non-locked
  backend — a guaranteed path to state corruption or loss with multiple
  engineers applying changes.

## Production Notes

`prod` Terraform applies require a second reviewer's approval (per
[`ci-cd/`](../ci-cd/README.md) environment promotion gates) and are never
run from an individual engineer's local machine — only via the CI/CD
pipeline's service account.

---

## Folder structure

```
13-infrastructure/
├── README.md                                    This file
├── 01-terraform-folder-structure.md              Repo layout standard
├── 02-backend-and-remote-state.md                 Backend, remote state, locking
├── 03-naming-and-tagging-standards.md             Terraform-enforced naming/tagging
├── 04-module-usage-guide.md                        How phases consume root terraform/ modules
├── 05-environment-promotion.md                     dev → qa → stage → prod flow
├── 06-state-management-and-locking.md              State operations procedure
└── 07-execution-checklist.md                       Per-environment provisioning checklist
```

See also: [`terraform/`](../terraform/README.md) for the actual reusable
module code this folder's standards govern.
