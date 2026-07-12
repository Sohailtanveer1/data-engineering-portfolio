# Audit Logging

**Purpose:** Configure Cloud Audit Logs to meet or exceed the audit
capability documented in
[`03-current-environment/06-security-configuration-assessment.md`](../03-current-environment/06-security-configuration-assessment.md)
— explicitly closing the gap if Ranger audit logging was found
insufficient or untested.
**Owner:** Security Engineering.

---

## Audit log types and default status

| Log Type | What It Captures | Enabled by Default? |
|---|---|---|
| Admin Activity | Resource/IAM policy changes (e.g., who created a bucket, who changed an IAM binding) | Yes, always on, cannot be disabled |
| Data Access | Reads/writes of actual data (e.g., who read a specific GCS object, who queried a BigQuery table) | **No — must be explicitly enabled per service** |
| System Event | GCP-internal automated actions | Yes, always on |
| Policy Denied | Access attempts denied by IAM | Yes, always on |

**Data Access logs must be explicitly enabled** for GCS, BigQuery, and
Secret Manager in every environment handling Restricted/Confidential data
— this is the single most commonly missed audit logging configuration
step in GCP deployments, since it is not on by default and produces no
error or warning if left off.

## Configuration

```hcl
# Terraform excerpt — see 13-infrastructure/ for full module
resource "google_project_iam_audit_config" "data_access_logging" {
  project = var.project_id
  service = "allServices"

  audit_log_config {
    log_type = "DATA_READ"
  }
  audit_log_config {
    log_type = "DATA_WRITE"
  }
}
```

## Log retention and export

| Requirement | Configuration |
|---|---|
| Retention | Cloud Logging default retention extended to match the compliance-required audit retention period from [`01-discovery/inventories/04-data-retention-and-compliance.md`](../01-discovery/inventories/04-data-retention-and-compliance.md) |
| Export destination | Log sink to a dedicated, access-restricted BigQuery dataset or GCS bucket for long-term retention beyond Cloud Logging's operational window, and for SIEM integration if the company has an existing SIEM |
| Immutability | Export bucket/dataset configured with retention policy / object lock to prevent tampering, satisfying the SOX audit trail requirement (constraint C2) |

## Validating audit logging actually works

Before this document is considered gated, run an explicit test: perform a
known data access action (e.g., read a specific object from a
Restricted-classified bucket) and confirm the corresponding Data Access
audit log entry appears, with correct identity, timestamp, and resource
detail — do not assume configuration alone guarantees correct behavior;
the current platform's audit gap (per
[`01-discovery/questions/03-security-team.md`](../01-discovery/questions/03-security-team.md)
Q10 — "has an audit log ever been used in an actual investigation")
suggests this kind of validation may never have been performed on-prem,
which is exactly the gap this migration should close.

## Common Mistakes

- Assuming "Cloud Audit Logs" being mentioned in GCP documentation means
  full data access logging is automatically active — Admin Activity
  logging being always-on is easily confused with Data Access logging,
  which is not.
- Enabling Data Access logging but never actually testing that a query
  against production data produces a findable, correctly-attributed log
  entry.

## Production Notes

Schedule a periodic (e.g., quarterly) audit log review specifically for
`fraud` and `finance` domain access, cross-referenced against the expected
service account/job access pattern — an unexpected access pattern in these
domains warrants immediate investigation, not just log retention for a
hypothetical future audit.
