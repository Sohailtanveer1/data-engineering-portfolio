# Permissions & Metadata Migration

**Purpose:** Define how HDFS POSIX permissions/ACLs and Ranger policies
(documented in
[`01-discovery/inventories/11-storage-inventory.md`](../01-discovery/inventories/11-storage-inventory.md)
and
[`03-current-environment/06-security-configuration-assessment.md`](../03-current-environment/06-security-configuration-assessment.md))
map to the target GCS IAM model designed in
[`10-security/`](../10-security/README.md) — this is not a mechanical 1:1
port, since the underlying access control models differ structurally.
**Owner:** Security Engineering + Platform Engineering.

---

## Why this isn't a direct port

HDFS uses POSIX-style owner/group/other permissions plus optional Ranger
policies layered on top, evaluated per-request against a Kerberos-
authenticated principal. GCS uses IAM bindings (role grants to principals —
users, groups, or service accounts) at the bucket or object level, with no
native POSIX permission bit concept. A mechanical attempt to preserve
"exact" permissions is neither possible nor desirable — instead, the
*intent* behind each HDFS permission/Ranger policy must be identified and
re-expressed as an equivalent (or improved) IAM policy.

## Mapping process, per data domain

1. **Extract current effective access.** For each HDFS path in
   [`01-discovery/inventories/11-storage-inventory.md`](../01-discovery/inventories/11-storage-inventory.md),
   list: POSIX owner/group/permissions, and any Ranger policy granting
   access beyond or instead of the POSIX defaults.
2. **Identify the actual principals** (service accounts, human users/
   groups) with access, and what they're allowed to do (read/write/
   execute-equivalent).
3. **Map each principal to its GCP equivalent** — a service account
   (created and scoped per
   [`10-security/`](../10-security/README.md)) for each on-prem service
   account/functional ID, and a Google Group (synced from AD/LDAP if
   federated, per
   [`07-security-architecture-overview.md`](../04-target-architecture/07-security-architecture-overview.md))
   for each human-user group.
4. **Assign IAM roles at the appropriate level** — bucket-level for
   broad domain access, object-prefix-level (via IAM Conditions) for
   finer-grained access where the current Ranger policy is more granular
   than a simple bucket-level grant would allow.
5. **Record the mapping explicitly** in the table below — this becomes
   part of the audit trail proving access wasn't inadvertently widened
   during migration.

## Mapping table template

| HDFS Path | Current POSIX Owner/Group | Current Ranger Policy | Principals with Access | GCP Target Bucket | GCS IAM Binding(s) | Access Narrowed/Same/Widened? |
|---|---|---|---|---|---|---|
| `/data/pricing/` | `svc_pricing_etl:pricing_team` | `ranger-policy-pricing-01` (read: pricing_team, write: svc_pricing_etl) | `svc_pricing_etl`, `pricing_team` group | `gs://acme-prod-pricing-raw/` | `roles/storage.objectAdmin` → `svc-pricing-etl@...`; `roles/storage.objectViewer` → `pricing-team@company.com` group | Same |

_(Populate exhaustively for every domain in
[`01-discovery/inventories/11-storage-inventory.md`](../01-discovery/inventories/11-storage-inventory.md).)_

## Mandatory review: no silent access widening

Every mapping row must be explicitly reviewed to confirm the "Access
Narrowed/Same/Widened" column — **any row marked "Widened" requires
explicit Security Engineering sign-off** before migration proceeds for
that domain. A common, easy-to-miss failure mode is granting a broader
IAM role (e.g., `roles/storage.admin` instead of a scoped custom role)
"to keep things simple," which silently widens access relative to a
tightly-scoped Ranger policy.

## Metadata migration

Beyond permissions, the following metadata must also be explicitly
addressed, not silently dropped:

| Metadata Type | On-Prem Source | GCS Target Approach |
|---|---|---|
| File modification timestamps | HDFS mtime | Preserved automatically by DistCp/STS transfer; verify post-transfer |
| Custom extended attributes (if used) | HDFS xattrs | No direct GCS equivalent — map to GCS object custom metadata key-value pairs if functionally required |
| HDFS storage policy (hot/warm/cold tiering) | HDFS storage policy | Mapped to GCS storage class + lifecycle policy per [`04-target-architecture/04-storage-architecture.md`](../04-target-architecture/04-storage-architecture.md) zoning |

## Common Mistakes

- Granting `roles/storage.admin` (full bucket control) broadly "to avoid
  permission errors during testing," then forgetting to narrow it before
  production cutover.
- Missing the mapping for functional/service IDs specifically — human
  access tends to get reviewed carefully, but a "just make the job work"
  mentality often over-grants service account permissions without the
  same scrutiny.

## Production Notes

For Tier 1 domains, the IAM mapping must be reviewed and signed off by
Security Engineering **before** that domain's storage migration wave is
executed, not retrofitted afterward — access control gaps in `fraud` and
`finance` domains are the highest-consequence category of oversight in
this entire migration.
