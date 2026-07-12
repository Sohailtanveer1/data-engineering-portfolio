# Module Usage Guide

**Purpose:** Explain how the per-environment configurations in
`terraform/environments/<env>/` consume the reusable modules in
[`terraform/modules/`](../terraform/README.md), with a worked example.
**Owner:** Cloud/DevOps.

---

## Example: composing the pricing data domain in `prod`

```hcl
# terraform/environments/prod/main.tf (excerpt)

module "pricing_raw_bucket" {
  source       = "../../modules/gcs-bucket"
  bucket_name  = "acme-prod-pricing-raw"
  location     = var.region
  storage_class = "STANDARD"
  kms_key_id   = module.pricing_kms_key.key_id
  data_domain  = "pricing"
  criticality_tier = "1"
  environment  = "prod"
  cost_center  = "data-platform"
}

module "pricing_curated_bucket" {
  source       = "../../modules/gcs-bucket"
  bucket_name  = "acme-prod-pricing-curated"
  location     = var.region
  storage_class = "STANDARD"
  kms_key_id   = module.pricing_kms_key.key_id
  data_domain  = "pricing"
  criticality_tier = "1"
  environment  = "prod"
  cost_center  = "data-platform"
}

module "pricing_kms_key" {
  source     = "../../modules/kms-keyring"
  key_ring   = "prod-keyring"
  key_name   = "pricing-cmek"
  rotation_period = "7776000s"  # 90 days, per 10-security/07-key-rotation.md
}

module "pricing_etl_service_account" {
  source       = "../../modules/iam-service-account"
  account_id   = "svc-pricing-etl"
  display_name = "Pricing ETL Service Account"
  project_roles = [
    "roles/dataproc.worker",
  ]
  bucket_bindings = {
    (module.pricing_raw_bucket.bucket_name)     = "roles/storage.objectViewer"
    (module.pricing_curated_bucket.bucket_name) = "roles/storage.objectAdmin"
  }
}

module "pricing_nightly_cluster_config" {
  source          = "../../modules/dataproc-cluster"
  job_family      = "pricing-nightly"
  environment     = "prod"
  machine_type    = "n2-standard-16"
  min_workers     = 4
  max_workers     = 12
  preemptible_max = 20
  service_account = module.pricing_etl_service_account.email
  subnetwork      = data.google_compute_subnetwork.dataproc_subnet.self_link
}
```

Every value here traces back to a specific design decision documented
elsewhere in this repository — the bucket naming to
[`04-target-architecture/04-storage-architecture.md`](../04-target-architecture/04-storage-architecture.md),
the KMS rotation period to
[`10-security/07-key-rotation.md`](../10-security/07-key-rotation.md), the
cluster sizing to
[`12-cluster-design/02-node-sizing-and-machine-types.md`](../12-cluster-design/02-node-sizing-and-machine-types.md)
— Terraform code should never introduce a new, undocumented design
decision; it implements decisions already made and reviewed elsewhere.

## Module versioning within the monorepo

Since modules and environment configurations live in the same repository
(not published as an independently-versioned registry module in this
setup), module changes take effect the next time an environment's
Terraform is applied — this makes the `dev` → `qa` → `stage` → `prod`
promotion sequence in
[`05-environment-promotion.md`](05-environment-promotion.md) the primary
safety mechanism for module changes, rather than a version pin.

## Common Mistakes

- Passing a value directly (a hardcoded bucket name, a hardcoded project
  ID) into a module call instead of referencing a variable or another
  module's output — this reintroduces hardcoding at the composition layer
  even if individual modules are themselves clean.
- Skipping the `dev`/`qa` proving step for a module change and applying
  directly to `prod` "since it's a small change" — see
  [`05-environment-promotion.md`](05-environment-promotion.md) for why
  this is never acceptable for `prod`.

## Production Notes

For any change to a module used by a Tier 1 job family's infrastructure,
require the `terraform plan` output to be reviewed line-by-line by a
second engineer before promotion to `stage`/`prod` — not just a glance at
the diff summary.
