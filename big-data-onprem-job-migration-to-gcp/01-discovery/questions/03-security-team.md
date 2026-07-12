# Discovery Questions — Security Team

**Purpose:** The current on-prem security model (typically Kerberos +
Ranger + LDAP/AD integration) must be fully understood before we can design
an equivalent-or-better IAM model on GCP. Getting this wrong is the
single highest-severity risk category in the program (see R5 in
[`00-project-overview/07-risk-register-summary.md`](../../00-project-overview/07-risk-register-summary.md)).
**Owner:** Migration Program Lead, conducted with Security Engineering lead.
**Audience:** InfoSec, security engineering, compliance liaison if separate.
**Inputs:** Current Ranger policies export, Kerberos principal list (if
extractable), any existing security audit reports.
**Outputs:** Directly feeds [`10-security/`](../../10-security/README.md)
and the compliance section of
[`04-data-retention-and-compliance.md`](../inventories/04-data-retention-and-compliance.md).

---

## Questions

| # | Question | Why we ask it |
|---|---|---|
| 1 | What data classification levels exist (e.g., public, internal, confidential, restricted/PII), and which datasets on this platform fall into each? | Classification directly determines encryption, access control, and residency requirements in [`10-security/`](../../10-security/README.md) — this cannot be designed generically. |
| 2 | Which datasets contain PII, PCI-scoped, or otherwise regulated data (payment info, customer PII, health data if applicable)? | Regulated data may have specific GCP configuration requirements (CMEK, VPC-SC, specific regions) that must be designed in from the start, not retrofitted. |
| 3 | What are the current Ranger/Sentry policies — who can access what, and how granular is enforcement (database, table, column, row-level)? | GCP IAM's access model differs structurally from Ranger; understanding current granularity is required to avoid quietly widening access during migration. |
| 4 | How are service accounts / functional IDs currently managed, and how many exist? | Every on-prem functional ID needs a deliberate GCP service-account equivalent with least-privilege scoping — an inventory here prevents ad-hoc account sprawl later. |
| 5 | What is the current audit logging setup — what's captured, how long is it retained, and has it ever been used in an actual investigation? | Sets the bar [`10-security/`](../../10-security/README.md) audit logging (Cloud Audit Logs) must meet or exceed. |
| 6 | What compliance frameworks apply to this platform today (PCI-DSS, SOX, GDPR/CCPA, others)? | Determines mandatory controls (encryption at rest/in transit, key rotation, data residency) that are non-negotiable in the target design. |
| 7 | Are there existing data residency requirements (data must not leave a specific region/country)? | Directly constrains GCP region selection in [`04-target-architecture/`](../../04-target-architecture/README.md). |
| 8 | How is encryption currently handled at rest and in transit? | Sets the baseline [`10-security/`](../../10-security/README.md) KMS/encryption design must match or exceed. |
| 9 | What is the incident response process today if a data breach or unauthorized access is detected on this platform? | The new platform needs an equivalent, GCP-native incident response path, not a gap. |
| 10 | Has this platform undergone a security audit or penetration test? What were the findings, and were they remediated? | Known unremediated findings should not be carried forward into the new platform by default. |
| 11 | Who has emergency/break-glass access today, and how is it logged? | GCP needs an equivalent, auditable break-glass IAM pattern designed deliberately, not left ad-hoc. |
| 12 | What is the required key rotation policy, and is it currently being met? | Feeds Cloud KMS rotation policy design in [`10-security/`](../../10-security/README.md). |

## Validation of answers

Request the actual exported Ranger policy files and a sample of Cloud Audit
Log-equivalent on-prem audit records, rather than relying solely on verbal
description — policies drift from documentation over time.
