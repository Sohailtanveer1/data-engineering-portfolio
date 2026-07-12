# Terraform Pipeline

**Purpose:** The concrete pipeline for validating, planning, and applying
Terraform changes — implementing
[`13-infrastructure/05-environment-promotion.md`](../13-infrastructure/05-environment-promotion.md)
and
[`13-infrastructure/06-state-management-and-locking.md`](../13-infrastructure/06-state-management-and-locking.md)
as an automated pipeline.
**Owner:** Cloud/DevOps.

---

## Pipeline stages

| Stage | What Runs | Gate |
|---|---|---|
| Format Check | `terraform fmt -check -recursive` | Fails on any unformatted file |
| Validate | `terraform validate` per module/environment | Fails on any syntax/config error |
| Lint | `tflint`, checking for GCP-specific best practice violations | Fails on any violation |
| Security Scan | `tfsec` or `checkov`, checking for insecure configuration patterns (e.g., a bucket without CMEK, an overly broad IAM binding) | Fails on any High/Critical finding |
| Plan | `terraform plan` against the target environment, output posted as a PR comment for review | Human review of the plan required before merge |
| Apply (dev) | Automatic on merge to `main` | None — `dev` is the proving ground |
| Apply (qa/stage/prod) | Manual trigger, per [`13-infrastructure/05-environment-promotion.md`](../13-infrastructure/05-environment-promotion.md) gates | Second approver required for `prod` |

## Naming/tagging validation

The pipeline's `validate` and `plan` stages surface any naming convention
or mandatory tagging violation caught by the module-level variable
validation blocks defined in
[`13-infrastructure/03-naming-and-tagging-standards.md`](../13-infrastructure/03-naming-and-tagging-standards.md)
— these fail the pipeline the same as any other validation error, not
just a warning.

## Drift detection

A **scheduled** (not just PR-triggered) pipeline run performs
`terraform plan` against every environment on a recurring basis (e.g.,
daily), alerting if any drift is detected (a plan showing changes when
none were expected indicates something was modified outside Terraform) —
this directly enforces constraint C5 (all infrastructure via Terraform)
on an ongoing basis, not just at change time.

## Example workflow reference

See [`workflows/terraform-ci.yml`](workflows/terraform-ci.yml) for the
full working GitHub Actions implementation.

## Common Mistakes

- Skipping the `tfsec`/`checkov` security scan stage as "too noisy" —
  tune the tool's rule set to reduce false positives rather than removing
  the check entirely.
- Not implementing scheduled drift detection, missing out-of-band changes
  until they cause a confusing `terraform plan` diff during an unrelated
  future change.

## Production Notes

`prod` Terraform applies always run via this pipeline's service account,
never a human's local credentials, even during an emergency change (per
the expedited process in
[`13-infrastructure/05-environment-promotion.md`](../13-infrastructure/05-environment-promotion.md))
— emergency speed comes from expediting pipeline approval, not bypassing
the pipeline.
