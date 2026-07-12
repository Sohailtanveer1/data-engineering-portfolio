# Security Execution & Review Checklist (Per Data Domain)

**Purpose:** A single checklist confirming every security control in this
folder has been applied to a given data domain before that domain's data
migration proceeds to production, per constraint C3.
**Owner:** Security Engineering (approver), Platform Engineering
(executor).

---

## Checklist — Data Domain: `_______________`

### IAM & Service Accounts

- [ ] Custom IAM roles defined and reviewed per
      [`01-iam-design.md`](01-iam-design.md)
- [ ] Service account created per
      [`02-service-account-strategy.md`](02-service-account-strategy.md),
      one per job family, least-privilege scoped
- [ ] No broad predefined roles (`editor`, `owner`, `storage.admin`)
      assigned in `prod`
- [ ] Human access via Google Groups only, no individual bindings in `prod`
- [ ] IAM mapping from
      [`05-storage-migration/06-permissions-and-metadata-migration.md`](../05-storage-migration/06-permissions-and-metadata-migration.md)
      shows no unreviewed "Widened" access

### Secrets

- [ ] Every credential for this domain migrated to Secret Manager per
      [`03-secret-manager-design.md`](03-secret-manager-design.md)
- [ ] Original plaintext credential revoked/rotated at source
- [ ] Secret access scoped to only the service accounts that need it

### Encryption

- [ ] CMEK applied per
      [`04-kms-and-encryption.md`](04-kms-and-encryption.md) if domain is
      Restricted/Confidential classified
- [ ] Key access policy reviewed and approved

### Audit Logging

- [ ] Data Access audit logging enabled per
      [`05-audit-logging.md`](05-audit-logging.md) for every service
      handling this domain's data
- [ ] Audit logging validated with a live test (not assumed from
      configuration alone)
- [ ] Log export/retention configured per compliance requirement

### Break-Glass & Policies

- [ ] No standing human data-plane access to `prod` for this domain
- [ ] Break-glass process confirmed applicable and rehearsed

### Rotation

- [ ] Rotation cadence assigned per
      [`07-key-rotation.md`](07-key-rotation.md) for every secret/key in
      this domain

### Sign-off

- [ ] Reviewed and approved by Security Engineering
- [ ] Reviewed by Platform Engineering
- [ ] Recorded in [`14-job-migration/`](../14-job-migration/README.md)
      tracker as a gate passed for this domain's jobs

**Reviewed by (Security):** ________________ **Date:** ________________
**Executed by (Platform):** ________________ **Date:** ________________

## Common Mistakes

- Treating this checklist as a formality to complete quickly under
  schedule pressure — per constraint C3, this is a **hard gate**, not a
  best-effort review; production data migration for a domain must not
  proceed without every item confirmed.
