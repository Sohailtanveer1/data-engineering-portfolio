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
    job_family       = var.job_family
  }

  # HA mode uses 3 masters per 12-cluster-design/05-high-availability-design.md;
  # standard ephemeral clusters use a single master.
  master_count = var.is_ha_cluster ? 3 : 1
}

resource "google_dataproc_autoscaling_policy" "this" {
  policy_id = "${var.job_family}-${var.environment}-autoscaling"
  project   = var.project_id
  location  = var.region

  worker_config {
    min_instances = var.min_workers
    max_instances = var.max_workers
    weight        = 1
  }

  secondary_worker_config {
    min_instances = 0
    max_instances = var.preemptible_max_workers
    weight        = 1
  }

  basic_algorithm {
    yarn_config {
      graceful_decommission_timeout = "3600s"
      scale_up_factor                = 0.5
      scale_down_factor              = 0.5
      scale_up_min_worker_fraction   = 0.0
      scale_down_min_worker_fraction = 0.0
    }
    cooldown_period = "120s"
  }
}

resource "google_dataproc_cluster" "this" {
  name    = "${var.job_family}-${var.environment}"
  project = var.project_id
  region  = var.region
  labels  = local.mandatory_labels

  cluster_config {
    staging_bucket = null # uses default staging bucket unless explicitly overridden by the caller

    gce_cluster_config {
      subnetwork       = var.subnetwork_self_link
      service_account  = var.service_account_email
      internal_ip_only = true # no public IPs, per 11-network/02-firewall-rules.md
      service_account_scopes = [
        "https://www.googleapis.com/auth/cloud-platform",
      ]
    }

    master_config {
      num_instances = local.master_count
      machine_type  = var.master_machine_type
    }

    worker_config {
      num_instances = var.min_workers
      machine_type  = var.machine_type
    }

    autoscaling_config {
      policy_uri = google_dataproc_autoscaling_policy.this.id
    }

    dynamic "initialization_action" {
      for_each = var.initialization_action_scripts
      content {
        script      = initialization_action.value
        timeout_sec = 300
      }
    }

    software_config {
      override_properties = {
        "spark:spark.sql.adaptive.enabled" = "true"
      }
    }
  }
}
