# Example environment composition — pricing data domain, dev environment.
# See 13-infrastructure/04-module-usage-guide.md for the full narrative
# walkthrough of this file.

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
  }

  backend "gcs" {
    bucket = "acme-data-platform-shared-services-tfstate"
    prefix = "data-platform/dev"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  type        = string
  description = "GCP project ID for the dev environment."
}

variable "region" {
  type        = string
  default     = "us-central1"
  description = "Primary region for dev resources."
}

variable "subnetwork_self_link" {
  type        = string
  description = "Self-link of the dataproc-subnet in this environment's VPC, per 11-network/01-vpc-and-subnet-design.md."
}

module "pricing_kms_key" {
  source = "../../modules/kms-keyring"

  project_id    = var.project_id
  location      = var.region
  key_ring_name = "dev-keyring"
  key_name      = "pricing-cmek"
}

module "pricing_raw_bucket" {
  source = "../../modules/gcs-bucket"

  bucket_name      = "acme-dev-pricing-raw"
  project_id       = var.project_id
  location         = var.region
  kms_key_id       = module.pricing_kms_key.key_id
  data_domain      = "pricing"
  criticality_tier = "1"
  environment      = "dev"

  lifecycle_rules = [
    { age_days = 90, action_type = "SetStorageClass", target_storage_class = "NEARLINE" },
  ]
}

module "pricing_curated_bucket" {
  source = "../../modules/gcs-bucket"

  bucket_name      = "acme-dev-pricing-curated"
  project_id       = var.project_id
  location         = var.region
  kms_key_id       = module.pricing_kms_key.key_id
  data_domain      = "pricing"
  criticality_tier = "1"
  environment      = "dev"
}

module "pricing_etl_service_account" {
  source = "../../modules/iam-service-account"

  project_id   = var.project_id
  account_id   = "svc-pricing-etl"
  display_name = "Pricing ETL Service Account (dev)"

  bucket_bindings = {
    (module.pricing_raw_bucket.bucket_name)     = "roles/storage.objectViewer"
    (module.pricing_curated_bucket.bucket_name) = "roles/storage.objectAdmin"
  }

  secret_bindings = {
    "pricing-db-password-dev" = "roles/secretmanager.secretAccessor"
  }
}

module "pricing_nightly_cluster" {
  source = "../../modules/dataproc-cluster"

  project_id             = var.project_id
  region                 = var.region
  job_family             = "pricing-nightly"
  environment             = "dev"
  subnetwork_self_link   = var.subnetwork_self_link
  service_account_email  = module.pricing_etl_service_account.email
  machine_type           = "n2-standard-4" # smaller than prod sizing for dev cost efficiency
  min_workers            = 2
  max_workers            = 4
  preemptible_max_workers = 4
  data_domain            = "pricing"
  criticality_tier       = "1"
}

output "pricing_etl_service_account_email" {
  value = module.pricing_etl_service_account.email
}

output "pricing_nightly_cluster_name" {
  value = module.pricing_nightly_cluster.cluster_name
}
