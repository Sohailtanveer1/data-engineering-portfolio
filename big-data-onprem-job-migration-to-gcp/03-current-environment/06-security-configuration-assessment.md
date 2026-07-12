# Security Configuration Assessment (As-Deployed)

**Purpose:** Document the *actual, currently enforced* security
configuration — Kerberos, Ranger, LDAP/AD integration — as opposed to the
policy-level questions already covered in
[`01-discovery/questions/03-security-team.md`](../01-discovery/questions/03-security-team.md).
Policy documents describe intent; this document describes what's actually
configured and running, which frequently differs. This is the direct
technical baseline for
[`10-security/`](../10-security/README.md) IAM design.
**Owner:** Platform Engineering, with Security Engineering review.
**Inputs:** `core-site.xml`/`hdfs-site.xml` security sections, KDC
configuration, Ranger policy export, LDAP/AD integration configuration.

---

## Authentication

| Setting | Current Value |
|---|---|
| Kerberos enabled cluster-wide? | |
| KDC type (MIT Kerberos / Active Directory-integrated) | |
| Keytab management process (how are service keytabs distributed/rotated?) | |
| Number of active service principals | |
| LDAP/AD integration for human user authentication? | |

## Authorization

| Setting | Current Value |
|---|---|
| Ranger (or Sentry) deployed? | |
| Ranger policy count (approx.) | |
| Granularity in practice (database/table/column/row-level policies actually in use, not just supported) | |
| Any known overly-broad policies (e.g., wildcard grants)? | |
| Policy review/audit cadence | |

## Encryption

| Setting | Current Value |
|---|---|
| HDFS Transparent Data Encryption (TDE) enabled? Which zones? | |
| Encryption in transit (RPC encryption, HTTPS for web UIs) enabled? | |
| Key management system in use (Hadoop KMS, HSM, other)? | |

## Audit logging

| Setting | Current Value |
|---|---|
| Ranger audit logging enabled and where stored (HDFS, Solr, external SIEM)? | |
| HDFS audit log enabled? | |
| Audit log retention period | |
| Has an audit log ever been used in an actual investigation? (cross-check against [`01-discovery/questions/03-security-team.md`](../01-discovery/questions/03-security-team.md) Q10) | |

## Service account / functional ID inventory

| Service Account | Purpose | Keytab Location | Scope of Access (broad summary) |
|---|---|---|---|
| `svc_pricing_etl` | Pricing ETL jobs | | |
| `svc_fraud_etl` | Fraud ETL jobs | | |

_(Cross-reference against [`01-discovery/inventories/11-storage-inventory.md`](../01-discovery/inventories/11-storage-inventory.md)
permissions snapshot; every service account there should appear here with
full detail.)_

## Gap analysis: as-deployed vs. as-documented policy

| Area | Documented Policy Says | Actual Configuration Shows | Gap? |
|---|---|---|---|
| _(e.g., "all PII columns must be masked")_ | | | |

This table is the most important output of this document — it surfaces
exactly where current practice has drifted from policy, which
[`10-security/`](../10-security/README.md) must decide to either
deliberately correct (tightening on GCP) or explicitly accept and
document as a conscious risk decision, never silently carry forward
unexamined.

## Common Mistakes

- Documenting Ranger's *capability* (what it could enforce) instead of its
  *actual configured policies* (what it does enforce today).
- Assuming Kerberos being "enabled" means every service account
  consistently uses it — partial adoption (some jobs running with
  Kerberos disabled or using a shared, over-privileged keytab) is common
  and must be explicitly checked, not assumed.

## Production Notes

Any gap found in the pricing, fraud, or finance data domains between
documented policy and actual configuration should be escalated to Security
immediately, independent of the migration timeline — these are the domains
where a security gap has the most direct business and compliance
consequence.
