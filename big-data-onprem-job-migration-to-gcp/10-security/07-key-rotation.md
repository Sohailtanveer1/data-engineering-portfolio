# Key Rotation Policy

**Purpose:** Define rotation cadence and automation for KMS keys and
Secret Manager secrets, meeting or exceeding the rotation policy
documented (or found absent) in
[`01-discovery/questions/03-security-team.md`](../01-discovery/questions/03-security-team.md)
Q12.
**Owner:** Security Engineering.

---

## KMS key rotation

| Key Type | Rotation Cadence | Automation |
|---|---|---|
| Data domain CMEK keys (`pricing-cmek`, `fraud-cmek`, etc.) | 90 days | Cloud KMS automatic rotation schedule, configured via Terraform |
| Secret Manager encryption key | 90 days | Cloud KMS automatic rotation schedule |

Cloud KMS automatic rotation creates a new key version on schedule;
**prior key versions remain available for decrypting data encrypted under
them** (KMS does not re-encrypt existing data automatically) — data
encrypted under an older key version remains readable, and new writes use
the latest version. This is a fundamentally different (and lower-risk)
model than manually replacing a key wholesale, and should be explained
clearly to any stakeholder unfamiliar with it during
[`documentation/`](../documentation/README.md) onboarding material.

## Secret Manager secret rotation

| Secret Category | Rotation Cadence | Process |
|---|---|---|
| Database credentials | Per the source system's own policy, or 90 days if the platform controls the credential | Automated where the source system supports programmatic credential rotation (e.g., Cloud SQL); manual, tracked process otherwise |
| API keys (third-party SaaS) | Per the vendor's supported rotation process, at minimum annually | Manual, tracked in [`documentation/`](../documentation/README.md), since most third-party rotation requires coordinated action with the vendor |
| Internal service-to-service credentials | 90 days | Automated via a scheduled Cloud Function/Composer DAG that generates a new credential, updates Secret Manager, and confirms the consuming service resolves it correctly before considering rotation complete |

Because `ConfigLoader` always resolves the `latest` secret version (per
[`07-spark-migration/05-configuration-management-and-secrets.md`](../07-spark-migration/05-configuration-management-and-secrets.md)),
rotating a secret's value requires **no job redeployment** — this is a key
design benefit that should be validated explicitly (rotate a non-critical
secret in `qa` and confirm the next job run picks up the new value without
any code/config change).

## Rotation failure handling

If a rotated credential fails validation (e.g., the new database password
doesn't authenticate successfully), the automation must **not** overwrite
the previously-working secret version until the new one is confirmed
working — always validate before promoting, never rotate-then-hope.

## Common Mistakes

- Enabling KMS automatic rotation and assuming this alone satisfies a
  compliance rotation requirement without documenting the actual rotation
  evidence (compliance auditors typically want to see rotation history,
  not just a policy setting).
- Rotating a secret without first confirming the consuming job/service can
  actually pick up the new value correctly — an untested rotation
  automation is itself a production risk.

## Production Notes

For `fraud` and `finance` domain secrets specifically, require rotation
automation to be tested in `qa` at least once before being relied upon in
`prod`, and require Security Engineering sign-off on the automation
design before enabling it for these domains' credentials.
