terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
  }
}

locals {
  mandatory_labels = {
    managed_by       = "terraform"
    environment      = var.environment
    data_domain      = var.data_domain
    criticality_tier = var.criticality_tier
    cost_center      = var.cost_center
  }
}

resource "google_storage_bucket" "this" {
  name                        = var.bucket_name
  project                     = var.project_id
  location                    = var.location
  storage_class                = var.storage_class
  uniform_bucket_level_access = true # required — no legacy ACLs, IAM only
  public_access_prevention    = "enforced"

  labels = local.mandatory_labels

  versioning {
    enabled = var.versioning_enabled
  }

  dynamic "encryption" {
    for_each = var.kms_key_id != null ? [1] : []
    content {
      default_kms_key_name = var.kms_key_id
    }
  }

  dynamic "lifecycle_rule" {
    for_each = var.lifecycle_rules
    content {
      condition {
        age = lifecycle_rule.value.age_days
      }
      action {
        type          = lifecycle_rule.value.action_type
        storage_class = lifecycle_rule.value.action_type == "SetStorageClass" ? lifecycle_rule.value.target_storage_class : null
      }
    }
  }
}
