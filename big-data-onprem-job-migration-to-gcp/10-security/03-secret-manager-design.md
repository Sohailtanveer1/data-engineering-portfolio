# Secret Manager Design

**Purpose:** Provide the concrete Secret Manager structure implementing
the pattern already established in
[`07-spark-migration/05-configuration-management-and-secrets.md`](../07-spark-migration/05-configuration-management-and-secrets.md)
and
[`09-composer-migration/06-variables-connections-and-secrets.md`](../09-composer-migration/06-variables-connections-and-secrets.md),
closing every plaintext-credential finding from
[`01-discovery/inventories/12-external-dependencies.md`](../01-discovery/inventories/12-external-dependencies.md).
**Owner:** Security Engineering.

---

## Secret inventory (migrated from plaintext findings)

| Secret Name | Purpose | Migrated From | Accessing Service Account(s) |
|---|---|---|---|
| `pricing-db-password-prod` | Pricing source DB credential | Sqoop password file (flagged ⚠ in Discovery) | `svc-pricing-etl@...` |
| `oms-reconciliation-db-password-prod` | OMS reconciliation DB credential | Sqoop password file | `svc-finance-etl@...` |
| `marketing-automation-api-key-prod` | Marketing SaaS API key | Job config file (flagged ⚠ in Discovery) | `svc-marketing-etl@...` |
| `vendor-sftp-private-key-prod` | Vendor SFTP integration key | SSH key on edge node | `svc-vendor-integration@...` |

_(Populate exhaustively from every ⚠-flagged item in
[`01-discovery/inventories/12-external-dependencies.md`](../01-discovery/inventories/12-external-dependencies.md)
— every flagged plaintext credential must have a corresponding Secret
Manager entry and a confirmed migration date.)_

## Access scoping

Every secret's IAM policy grants `roles/secretmanager.secretAccessor`
**only** to the specific service account(s) that need it — never a
platform-wide "all jobs can read all secrets" binding. This is enforced
via per-secret IAM policies managed in Terraform
([`13-infrastructure/`](../13-infrastructure/README.md)), not manually
via `gcloud`/Console.

## Secret versioning

- Every secret update creates a new version; the `ConfigLoader` (per
  [`07-spark-migration/05-configuration-management-and-secrets.md`](../07-spark-migration/05-configuration-management-and-secrets.md))
  always resolves the `latest` version, so rotation
  ([`07-key-rotation.md`](07-key-rotation.md)) requires no job redeployment.
- Prior versions are retained (not immediately destroyed) for a defined
  window to support rollback if a rotation introduces an issue.

## What does NOT belong in Secret Manager

- Non-secret configuration (bucket names, project IDs) — these belong in
  Composer Variables/job config YAML per the configuration layering model.
- Large binary blobs or files beyond typical credential/key size — Secret
  Manager is for secrets, not general file storage; a large certificate
  bundle or similar should be evaluated case-by-case with Security.

## Migration procedure per flagged plaintext credential

1. Create the secret in Secret Manager with the correct name and value.
2. Grant access to exactly the service account(s) that need it.
3. Update the consuming job's config to reference `secret://<secret-name>`
   per
   [`07-spark-migration/05-configuration-management-and-secrets.md`](../07-spark-migration/05-configuration-management-and-secrets.md).
4. Confirm the job successfully resolves the secret in a non-production
   test.
5. **Revoke/rotate the original plaintext credential** at its source
   system — migrating to Secret Manager without invalidating the old
   plaintext copy leaves the original exposure unresolved.

## Common Mistakes

- Migrating a credential to Secret Manager but leaving the original
  plaintext copy (in a config file, on an edge node) in place "just in
  case" — this doesn't close the security gap, it just adds a second,
  redundant credential path.
- Granting `roles/secretmanager.secretAccessor` at the project level
  instead of per-secret, effectively giving every service account access
  to every secret regardless of actual need.

## Production Notes

Treat every plaintext credential migration to Secret Manager as an
independent security remediation with its own tracked completion date —
do not bundle it silently into a broader job migration task where its
completion (or non-completion) could be lost from visibility.
