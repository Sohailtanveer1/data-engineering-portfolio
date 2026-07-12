# 10 — Security

## Purpose

Implement the security architecture principles from
[`04-target-architecture/07-security-architecture-overview.md`](../04-target-architecture/07-security-architecture-overview.md)
as concrete, provisioned IAM roles, service accounts, Secret Manager
structure, and KMS key hierarchy — closing every gap identified in
[`03-current-environment/06-security-configuration-assessment.md`](../03-current-environment/06-security-configuration-assessment.md)
and satisfying every compliance requirement from
[`01-discovery/inventories/04-data-retention-and-compliance.md`](../01-discovery/inventories/04-data-retention-and-compliance.md).

## Owner

**Security Engineering**, implemented jointly with Platform Engineering.

## Inputs

- Security architecture principles from
  [`04-target-architecture/07-security-architecture-overview.md`](../04-target-architecture/07-security-architecture-overview.md).
- As-deployed vs. policy gap analysis from
  [`03-current-environment/06-security-configuration-assessment.md`](../03-current-environment/06-security-configuration-assessment.md).
- Service account inventory from
  [`01-discovery/inventories/11-storage-inventory.md`](../01-discovery/inventories/11-storage-inventory.md)
  permissions snapshot.

## Outputs

- Complete IAM role and service account design, provisioned via Terraform.
- Secret Manager structure with every credential migrated off plaintext
  storage.
- KMS key hierarchy with CMEK applied per data classification.
- Audit logging configuration closing the gap (if any) found in Discovery.

## Prerequisites

[`04-target-architecture/`](../04-target-architecture/README.md) gated.

## Deliverables

1. IAM design (custom roles, group mappings).
2. Service account strategy (one per function, least privilege).
3. Secret Manager design.
4. KMS and encryption design.
5. Audit logging configuration.
6. Security policies and break-glass access mechanism.
7. Key rotation policy and automation.
8. Execution and review checklist.

## Risks

Every risk in this folder maps to R5 in
[`00-project-overview/07-risk-register-summary.md`](../00-project-overview/07-risk-register-summary.md)
— a security model gap here is Critical severity, not just High, given the
compliance and business sensitivity of the fraud/finance/PII data domains
involved.

## Rollback

IAM/Secret Manager/KMS changes are provisioned via Terraform and can be
reverted via standard Terraform state rollback — see
[`13-infrastructure/`](../13-infrastructure/README.md). No production data
migration is blocked or unblocked reversibly by this folder alone; it must
be gated **before** any production data migration per constraint C3 in
[`00-project-overview/06-assumptions-and-constraints.md`](../00-project-overview/06-assumptions-and-constraints.md).

## Validation

This folder requires a **formal security review sign-off** before any
production data crosses into GCP — not just internal Platform Engineering
self-review — per constraint C3.

## Best Practices

Design IAM roles around actual job/function needs (from the dependency
analysis and storage inventory), not by copying the current Ranger
policies' surface shape — this is an opportunity to tighten, not just
replicate.

## Lessons Learned

The most common post-migration security finding in comparable
Hadoop-to-cloud migrations is an over-broad IAM role granted "temporarily"
during testing that was never narrowed before production cutover.

## Common Mistakes

- Granting `roles/editor` or other broad predefined roles to service
  accounts "to unblock development" without a tracked plan to narrow them
  before production.
- Treating audit logging as "on by default" without explicitly verifying
  Data Access audit logs are enabled for the specific services handling
  Restricted-classified data.

## Production Notes

Every IAM binding touching `fraud`, `finance`, or PII-classified data
domains requires explicit Security Engineering review and sign-off before
being applied in `prod` — no exceptions, regardless of time pressure.

---

## Folder structure

```
10-security/
├── README.md                                       This file
├── 01-iam-design.md                                 Custom roles, group mappings
├── 02-service-account-strategy.md                   One per function, least privilege, Workload Identity
├── 03-secret-manager-design.md                       Secret structure and access scoping
├── 04-kms-and-encryption.md                          Key hierarchy, CMEK application
├── 05-audit-logging.md                                Data Access audit log configuration
├── 06-security-policies-and-break-glass.md            Human access model
├── 07-key-rotation.md                                 Rotation policy and automation
└── 08-execution-and-review-checklist.md               Per-domain security review checklist
```
