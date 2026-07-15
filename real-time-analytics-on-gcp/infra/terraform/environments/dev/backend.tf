# Remote state bucket comes from infra/terraform/bootstrap (run once,
# manually, before this). Terraform can't interpolate variables into a
# backend block, so the bucket name below must be typed literally —
# replace YOUR_PROJECT_ID after running bootstrap.
terraform {
  backend "gcs" {
    bucket = "YOUR_PROJECT_ID-tfstate"
    prefix = "environments/dev"
  }
}
