output "cluster_name" {
  value       = google_dataproc_cluster.this.name
  description = "The created cluster's name, for reference from a Composer DAG's DataprocSubmitJobOperator."
}

output "autoscaling_policy_id" {
  value       = google_dataproc_autoscaling_policy.this.id
  description = "The autoscaling policy ID, reusable across multiple cluster definitions in the same job family if needed."
}
