variable "project_id" {
  type        = string
  description = "GCP project ID."
}

variable "region" {
  type        = string
  description = "Region for the Dataproc cluster."
}

variable "job_family" {
  type        = string
  description = "Job family name, e.g. 'pricing-nightly' — used to derive the cluster name per 13-infrastructure/03-naming-and-tagging-standards.md."
}

variable "environment" {
  type        = string
  description = "Environment: dev, qa, stage, or prod."

  validation {
    condition     = contains(["dev", "qa", "stage", "prod"], var.environment)
    error_message = "environment must be one of: dev, qa, stage, prod."
  }
}

variable "subnetwork_self_link" {
  type        = string
  description = "Self-link of the private subnet this cluster launches into, per 11-network/01-vpc-and-subnet-design.md."
}

variable "service_account_email" {
  type        = string
  description = "Service account email this cluster's nodes run as, per 10-security/02-service-account-strategy.md."
}

variable "machine_type" {
  type        = string
  description = "Worker machine type, sized per 12-cluster-design/02-node-sizing-and-machine-types.md."
}

variable "master_machine_type" {
  type        = string
  default     = "n2-standard-4"
  description = "Master machine type. Single master for ephemeral clusters; overridden to HA (3 masters) for persistent clusters."
}

variable "min_workers" {
  type        = number
  description = "Minimum worker count for the autoscaling policy."
}

variable "max_workers" {
  type        = number
  description = "Maximum worker count for the autoscaling policy, per 12-cluster-design/03-autoscaling-policies.md."
}

variable "preemptible_max_workers" {
  type        = number
  default     = 0
  description = "Maximum secondary (preemptible/spot) worker count, capped per tier per 12-cluster-design/04-preemptible-and-spot-strategy.md."
}

variable "is_ha_cluster" {
  type        = bool
  default     = false
  description = "If true, provisions 3 master nodes (HA mode) — for persistent clusters per 12-cluster-design/05-high-availability-design.md. Ephemeral clusters should leave this false."
}

variable "initialization_action_scripts" {
  type        = list(string)
  default     = []
  description = "GCS URIs of initialization action scripts, per 12-cluster-design/07-initialization-actions-and-custom-images.md."
}

variable "data_domain" {
  type        = string
  description = "Owning data domain — applied as a mandatory label."
}

variable "criticality_tier" {
  type        = string
  description = "Criticality tier (1-4) — applied as a mandatory label."

  validation {
    condition     = contains(["1", "2", "3", "4"], var.criticality_tier)
    error_message = "criticality_tier must be one of: 1, 2, 3, 4."
  }
}

variable "cost_center" {
  type        = string
  default     = "data-platform"
  description = "Cost center label for billing attribution."
}
