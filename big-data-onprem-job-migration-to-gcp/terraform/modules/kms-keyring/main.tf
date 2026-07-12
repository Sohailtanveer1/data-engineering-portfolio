terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
  }
}

resource "google_kms_key_ring" "this" {
  project  = var.project_id
  name     = var.key_ring_name
  location = var.location
}

resource "google_kms_crypto_key" "this" {
  name            = var.key_name
  key_ring        = google_kms_key_ring.this.id
  rotation_period = var.rotation_period_seconds

  # Prior key versions remain available for decrypting data encrypted
  # under them — see 10-security/07-key-rotation.md for why this is
  # a lower-risk model than manual key replacement.
  lifecycle {
    prevent_destroy = true
  }
}

resource "google_kms_crypto_key_iam_member" "accessors" {
  for_each = toset(var.accessor_service_accounts)

  crypto_key_id = google_kms_crypto_key.this.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:${each.value}"
}
