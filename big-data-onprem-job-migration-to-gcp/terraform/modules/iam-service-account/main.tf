terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
  }
}

resource "google_service_account" "this" {
  project      = var.project_id
  account_id   = var.account_id
  display_name = var.display_name
}

# Project-level bindings — kept minimal per least-privilege; prefer the
# resource-scoped bindings below wherever possible.
resource "google_project_iam_member" "project_roles" {
  for_each = toset(var.project_roles)

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.this.email}"
}

# Bucket-scoped bindings (not project-wide storage.admin) — see
# 10-security/01-iam-design.md for why this granularity matters.
resource "google_storage_bucket_iam_member" "bucket_bindings" {
  for_each = var.bucket_bindings

  bucket = each.key
  role   = each.value
  member = "serviceAccount:${google_service_account.this.email}"
}

# Per-secret bindings — never a project-wide secretAccessor grant, per
# 10-security/03-secret-manager-design.md.
resource "google_secret_manager_secret_iam_member" "secret_bindings" {
  for_each = var.secret_bindings

  secret_id = each.key
  role      = each.value
  member    = "serviceAccount:${google_service_account.this.email}"
}
