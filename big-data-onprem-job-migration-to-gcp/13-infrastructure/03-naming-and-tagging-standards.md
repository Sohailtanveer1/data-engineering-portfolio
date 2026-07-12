# Naming & Tagging Standards (Terraform-Enforced)

**Purpose:** Enforce the naming convention from
[`04-target-architecture/02-landing-zone-and-project-structure.md`](../04-target-architecture/02-landing-zone-and-project-structure.md)
and the labeling requirement from
[`12-cluster-design/06-cluster-policies-and-governance.md`](../12-cluster-design/06-cluster-policies-and-governance.md)
programmatically, not just by convention.
**Owner:** Cloud/DevOps.

---

## Enforcement via variable validation

```hcl
# modules/gcs-bucket/variables.tf
variable "bucket_name" {
  type        = string
  description = "Bucket name, must follow <company>-<env>-<domain>-<zone> convention"

  validation {
    condition     = can(regex("^[a-z0-9-]+-(dev|qa|stage|prod)-[a-z0-9-]+-(raw|curated|archive)$", var.bucket_name))
    error_message = "Bucket name must match <company>-<env>-<domain>-<zone> (zone: raw|curated|archive)."
  }
}
```

Every module that creates a named resource includes this kind of
validation block — a Terraform plan/apply **fails fast** with a clear
error if naming convention is violated, rather than allowing an
inconsistently-named resource into production and catching it only in a
later manual review.

## Mandatory tags/labels

Every resource created by this Terraform codebase includes:

```hcl
locals {
  mandatory_labels = {
    managed_by        = "terraform"
    environment       = var.environment
    data_domain       = var.data_domain
    criticality_tier  = var.criticality_tier
    cost_center       = var.cost_center   # feeds 19-cost-optimization/ attribution
  }
}
```

Applied consistently via a shared `locals` block imported into every
module, not re-declared per module (avoiding the drift risk of
independently-maintained label sets across modules).

## Naming convention reference table

| Resource | Convention | Example |
|---|---|---|
| GCP Project | `<company>-data-platform-<env>` | `acme-data-platform-prod` |
| GCS Bucket | `<company>-<env>-<domain>-<zone>` | `acme-prod-pricing-curated` |
| Dataproc Cluster | `<job-family>-<env>` (or `-{{ ds_nodash }}` suffix for ephemeral, added at DAG submission time, not in the base Terraform-managed name) | `pricing-nightly-prod` |
| Service Account | `svc-<domain>-<function>@<project>.iam.gserviceaccount.com` | `svc-pricing-etl@acme-data-platform-prod.iam.gserviceaccount.com` |
| BigQuery Dataset | `<domain>_<env>` | `pricing_prod` |
| KMS Key Ring | `<env>-keyring` | `prod-keyring` |
| Terraform Module | `<gcp-service>-<purpose>` | `dataproc-ephemeral-cluster` |

This table is the single source of truth referenced by every phase
document in this repository that names a resource — if a naming decision
needs to change, it changes here first, then propagates.

## Common Mistakes

- Adding validation blocks to some modules but not others, leaving naming
  enforcement inconsistent across the codebase.
- Treating labels as optional metadata instead of a hard requirement — an
  unlabeled resource is invisible to
  [`19-cost-optimization/`](../19-cost-optimization/README.md) cost
  attribution reporting.

## Production Notes

Run a periodic (e.g., monthly) scripted audit of all `prod` resources
against the mandatory label requirement, catching any resource created
through an exceptional path (e.g., a GCP-managed resource created as a
side effect of another resource) that might not have gone through the
standard module and its validation.
