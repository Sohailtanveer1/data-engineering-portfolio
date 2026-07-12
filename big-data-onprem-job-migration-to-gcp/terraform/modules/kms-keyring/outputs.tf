output "key_id" {
  value       = google_kms_crypto_key.this.id
  description = "Full resource ID of the created crypto key, for use as a bucket/dataset CMEK reference."
}

output "key_ring_id" {
  value       = google_kms_key_ring.this.id
  description = "Full resource ID of the created key ring."
}
