# Security Architecture Overview

**Purpose:** Establish the high-level security design principles this
platform follows — full detail (IAM role definitions, Secret Manager
structure, KMS key hierarchy, audit logging configuration) lives in
[`10-security/`](../10-security/README.md); this document exists so
security is visibly a first-class part of the target architecture from the
start, not an appendix.
**Owner:** Security Engineering, reviewed by Migration Program Lead.
**Inputs:** [`01-discovery/questions/03-security-team.md`](../01-discovery/questions/03-security-team.md)
and
[`03-current-environment/06-security-configuration-assessment.md`](../03-current-environment/06-security-configuration-assessment.md)
findings — particularly the as-deployed-vs-policy gap analysis.

---

## Design principles

1. **Least privilege by default.** Every service account is scoped to
   exactly the resources it needs, mirroring (and where gaps were found in
   [`03-current-environment/06-security-configuration-assessment.md`](../03-current-environment/06-security-configuration-assessment.md),
   improving upon) the current Ranger policy granularity.
2. **No standing human access to production data by default.** Human
   access to `prod` resources is break-glass, time-boxed, and audited —
   not a standing role assignment. See
   [`10-security/`](../10-security/README.md) for the break-glass
   mechanism design.
3. **Secrets never live in code, config files, or DAGs.** Every credential
   goes through Secret Manager. This directly closes every plaintext-
   credential finding flagged in
   [`01-discovery/inventories/12-external-dependencies.md`](../01-discovery/inventories/12-external-dependencies.md).
4. **Encryption at rest via CMEK for all Restricted/Confidential data**,
   per the classification in
   [`01-discovery/inventories/04-data-retention-and-compliance.md`](../01-discovery/inventories/04-data-retention-and-compliance.md).
5. **Every access to production data is audit-logged**, closing the audit
   gap identified in
   [`03-current-environment/06-security-configuration-assessment.md`](../03-current-environment/06-security-configuration-assessment.md)
   if the current platform's audit logging is found insufficient.
6. **Security design is per-data-domain, not platform-wide uniform** —
   `fraud` and `finance` domains carry stricter access controls than
   `merchandising` reporting data, mirroring the classification work in
   [`01-discovery/`](../01-discovery/README.md).

## How this maps from the current Kerberos/Ranger model

| Current (Kerberos/Ranger) Concept | GCP Equivalent | Key Difference to Design For |
|---|---|---|
| Kerberos principal / keytab | Service Account + key or Workload Identity | No ticket expiry/renewal cycle to manage the same way — but keys need their own rotation policy |
| Ranger table/column/row-level policy | IAM (coarser) + BigQuery column/row-level security or Dataplex policy tags (finer) | GCP's finest-grained native controls are BigQuery-specific; Dataproc-Hive access control is coarser by comparison — factor this into the [`05-data-warehouse-architecture.md`](05-data-warehouse-architecture.md) decision for governance-sensitive tables |
| Ranger audit log | Cloud Audit Logs (Data Access logs) | Must be explicitly enabled per service — not on by default for data access logging |
| LDAP/AD group-based access | Cloud Identity / Google Groups synced from existing AD (if federated) | Requires confirming AD federation approach with IT/Identity team |

## Compliance mapping

Every compliance framework identified in
[`01-discovery/inventories/04-data-retention-and-compliance.md`](../01-discovery/inventories/04-data-retention-and-compliance.md)
(PCI-DSS, SOX, GDPR/CCPA as applicable) has a corresponding explicit
control design in [`10-security/`](../10-security/README.md) — this
overview does not restate that detail but confirms the principle: **no
compliance requirement identified in Discovery is left without an explicit
corresponding GCP control.**

## Common Mistakes

- Treating security architecture as something to finalize after compute
  and storage design is "done" — access control requirements (e.g.,
  column-level security needs) directly influence the BigQuery vs.
  Dataproc-Hive decision in
  [`05-data-warehouse-architecture.md`](05-data-warehouse-architecture.md)
  and must be considered together, not sequentially.
- Assuming GCP's default security posture is sufficient without explicit
  configuration — data access audit logging, for example, is not
  comprehensively on by default and must be deliberately enabled.

## Production Notes

Every gap identified in the as-deployed-vs-policy comparison in
[`03-current-environment/06-security-configuration-assessment.md`](../03-current-environment/06-security-configuration-assessment.md)
must have an explicit corresponding line item in
[`10-security/`](../10-security/README.md) showing how the target design
closes it — this traceability is required before
[`10-security/`](../10-security/README.md) can be considered gated.
