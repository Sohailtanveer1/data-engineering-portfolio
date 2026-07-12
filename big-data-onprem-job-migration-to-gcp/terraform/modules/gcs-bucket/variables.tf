variable "bucket_name" {
  type        = string
  description = "Bucket name, must follow <company>-<env>-<domain>-<zone> convention (zone: raw|curated|archive|scratch)."

  validation {
    condition     = can(regex("^[a-z0-9-]+-(dev|qa|stage|prod)-[a-z0-9-]+-(raw|curated|archive|scratch)$", var.bucket_name))
    error_message = "Bucket name must match <company>-<env>-<domain>-<zone> per 13-infrastructure/03-naming-and-tagging-standards.md."
  }
}

variable "project_id" {
  type        = string
  description = "GCP project ID this bucket is created in."
}

variable "location" {
  type        = string
  description = "Bucket location (region or multi-region), per 04-target-architecture/04-storage-architecture.md regional strategy."
}

variable "storage_class" {
  type        = string
  default     = "STANDARD"
  description = "Initial storage class. Lifecycle rules transition it over time per data domain retention policy."
}

variable "kms_key_id" {
  type        = string
  default     = null
  description = "Cloud KMS key self-link for CMEK. Required for Restricted/Confidential classified data domains, per 10-security/04-kms-and-encryption.md."
}

variable "lifecycle_rules" {
  description = "List of lifecycle rules (age-based storage class transition or deletion), per 19-cost-optimization/03-storage-cost-optimization.md."
  type = list(object({
    age_days           = number
    action_type        = string # "SetStorageClass" or "Delete"
    target_storage_class = optional(string)
  }))
  default = []
}

variable "versioning_enabled" {
  type        = bool
  default     = false
  description = "Enable object versioning. Recommended true for the Terraform state bucket and any bucket requiring rollback protection."
}

variable "data_domain" {
  type        = string
  description = "Owning data domain, e.g. 'pricing', 'fraud' — applied as a mandatory label."
}

variable "criticality_tier" {
  type        = string
  description = "Criticality tier (1-4) per 01-discovery/inventories/02-business-critical-jobs.md — applied as a mandatory label."

  validation {
    condition     = contains(["1", "2", "3", "4"], var.criticality_tier)
    error_message = "criticality_tier must be one of: 1, 2, 3, 4."
  }
}

variable "environment" {
  type        = string
  description = "Environment name: dev, qa, stage, or prod."

  validation {
    condition     = contains(["dev", "qa", "stage", "prod"], var.environment)
    error_message = "environment must be one of: dev, qa, stage, prod."
  }
}

variable "cost_center" {
  type        = string
  default     = "data-platform"
  description = "Cost center label for billing attribution, per 19-cost-optimization/01-cost-baseline-and-attribution.md."
}
