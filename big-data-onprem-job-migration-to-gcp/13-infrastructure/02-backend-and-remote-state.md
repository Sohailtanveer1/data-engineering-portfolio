# Backend & Remote State

**Purpose:** Configure a shared, locked, versioned remote state backend —
the foundation that makes multi-engineer, CI/CD-driven Terraform usage
safe.
**Owner:** Cloud/DevOps.

---

## Backend choice: GCS with state locking

```hcl
# environments/prod/backend.tf
terraform {
  backend "gcs" {
    bucket = "acme-data-platform-shared-services-tfstate"
    prefix = "data-platform/prod"
  }
}
```

GCS natively supports Terraform state locking (via object generation
preconditions) as of modern Terraform/provider versions, avoiding the need
for a separate DynamoDB-style locking mechanism (an AWS-specific pattern
not applicable here).

## One state file per environment, in the shared-services project

State files live in the `data-platform-shared-services` project (per
[`04-target-architecture/02-landing-zone-and-project-structure.md`](../04-target-architecture/02-landing-zone-and-project-structure.md)),
in a dedicated, tightly-access-controlled bucket:

```
gs://acme-data-platform-shared-services-tfstate/
├── data-platform/dev/default.tfstate
├── data-platform/qa/default.tfstate
├── data-platform/stage/default.tfstate
└── data-platform/prod/default.tfstate
```

Separate state files per environment (not one combined state) ensures a
`terraform apply` in `dev` can never accidentally affect `prod` resources
— consistent with the full environment isolation constraint (C4).

## State bucket protection

| Control | Configuration |
|---|---|
| Versioning | Enabled — every state change is recoverable |
| Access | IAM-scoped to only the CI/CD service account (write) and Cloud/DevOps team (read, for troubleshooting) — no broad access |
| Encryption | CMEK, consistent with [`10-security/04-kms-and-encryption.md`](../10-security/04-kms-and-encryption.md) |
| Deletion protection | Bucket-level protection against accidental deletion |

## State file sensitivity

Terraform state can contain sensitive values (e.g., a generated secret, if
any module output includes one) — treat the state bucket with the same
access rigor as
[`10-security/03-secret-manager-design.md`](../10-security/03-secret-manager-design.md)
secrets, and avoid outputting genuinely sensitive values from modules
where avoidable (reference Secret Manager secret names, not values,
wherever a module might otherwise be tempted to output a credential).

## Recovering from state issues

| Issue | Recovery |
|---|---|
| Accidental `terraform apply` with unintended changes | Revert via `terraform plan`/`apply` from the prior known-good configuration commit; use state versioning to inspect/restore a prior state version if needed |
| State lock stuck (e.g., a CI job was killed mid-apply) | `terraform force-unlock`, used only after confirming no other apply is genuinely in progress — a careless force-unlock during a real concurrent apply risks state corruption |
| State drift detected (real infrastructure doesn't match state) | `terraform plan` will surface the drift; investigate root cause (manual change? a resource modified outside Terraform?) before blindly applying to "fix" it |

## Common Mistakes

- Running `terraform force-unlock` reflexively whenever a lock is
  encountered, without confirming there isn't a genuine concurrent apply
  in progress — this is the most common cause of real state corruption.
- Combining multiple environments' resources into a single state file for
  "simplicity," eliminating the blast-radius protection separate state
  files provide.

## Production Notes

Any `prod` state operation beyond a standard CI/CD-driven apply (a manual
`terraform state` command, a force-unlock, an import) requires two-person
review before execution, given the potential for irreversible state
corruption.
