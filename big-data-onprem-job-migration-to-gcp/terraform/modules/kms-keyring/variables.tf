variable "project_id" {
  type        = string
  description = "GCP project ID this key ring is created in."
}

variable "location" {
  type        = string
  description = "KMS key ring location. Should match the region of resources it encrypts."
}

variable "key_ring_name" {
  type        = string
  description = "Key ring name, convention <env>-keyring per 13-infrastructure/03-naming-and-tagging-standards.md."
}

variable "key_name" {
  type        = string
  description = "Key name within the ring, e.g. 'pricing-cmek', per 10-security/04-kms-and-encryption.md domain-per-key design."
}

variable "rotation_period_seconds" {
  type        = string
  default     = "7776000s" # 90 days, per 10-security/07-key-rotation.md
  description = "Automatic key rotation period."
}

variable "accessor_service_accounts" {
  type        = list(string)
  default     = []
  description = "Service account emails granted roles/cloudkms.cryptoKeyEncrypterDecrypter on this key. Scoped per-domain, never platform-wide, per 10-security/01-iam-design.md."
}
