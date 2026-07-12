# IAM Design

**Purpose:** Define custom IAM roles and group mappings that replace the
Ranger policy granularity documented in
[`03-current-environment/06-security-configuration-assessment.md`](../03-current-environment/06-security-configuration-assessment.md),
scoped per data domain per the least-privilege principle.
**Owner:** Security Engineering.

---

## Role design principle

**Never use broad predefined roles** (`roles/editor`, `roles/owner`,
`roles/storage.admin`) for any service account or human group in `prod`.
Every role is either a narrowly-scoped predefined role (e.g.,
`roles/storage.objectViewer` on a specific bucket) or a custom role
defined for this platform's specific needs.

## Custom role catalog (illustrative — extend per actual need)

| Custom Role | Permissions | Assigned To |
|---|---|---|
| `dataPlatform.jobRunner` | `dataproc.jobs.create`, `dataproc.jobs.get`, storage read/write scoped to the job's specific bucket prefix | Per-job-family service accounts |
| `dataPlatform.pipelineOperator` | Composer DAG trigger/monitor permissions, no data-plane access | Composer's own service account |
| `dataPlatform.analystReader` | `bigquery.tables.getData` scoped to specific datasets, no write | Analyst Google Groups |
| `dataPlatform.securityAuditor` | Read-only access to IAM policies, audit logs, Secret Manager metadata (not secret values) | Security Engineering |

## Group-based access for humans

Human access is granted via Google Groups (synced from AD/LDAP if
federated, per
[`04-target-architecture/07-security-architecture-overview.md`](../04-target-architecture/07-security-architecture-overview.md)),
never direct individual user IAM bindings — this mirrors the current
LDAP/AD-group-based access pattern from
[`03-current-environment/06-security-configuration-assessment.md`](../03-current-environment/06-security-configuration-assessment.md)
and keeps access reviewable at the group level.

| Group | Access Level |
|---|---|
| `data-eng-pricing@company.com` | Full read/write on pricing domain resources in non-prod; read-only in prod (writes happen only via service accounts/CI-CD) |
| `data-eng-fraud@company.com` | Same pattern, fraud domain |
| `analysts-merchandising@company.com` | `dataPlatform.analystReader` scoped to merchandising datasets |
| `security-engineering@company.com` | `dataPlatform.securityAuditor` platform-wide |

## Mapping from the on-prem Ranger policy inventory

Every HDFS path/Ranger policy mapping documented in
[`05-storage-migration/06-permissions-and-metadata-migration.md`](../05-storage-migration/06-permissions-and-metadata-migration.md)
is the direct input to this IAM design — every mapping row's "Access
Narrowed/Same/Widened" determination must resolve to a specific IAM
binding recorded here.

## IAM Conditions for finer-grained scoping

Where a Ranger policy granted access at a finer granularity than a
bucket-level IAM binding naturally provides (e.g., access to only a
specific date-partition prefix), use IAM Conditions to express the
equivalent scope:

```
resource.name.startsWith("projects/_/buckets/acme-prod-pricing-curated/objects/daily_price_snapshot/")
```

## Common Mistakes

- Granting project-level IAM roles when a bucket- or dataset-level binding
  would suffice — broader scope than necessary, even if the role itself is
  narrowly permissioned, increases blast radius unnecessarily.
- Mapping every on-prem "read access" grant to `roles/storage.objectViewer`
  at the bucket level without checking whether the original Ranger policy
  was actually scoped more narrowly (per-table/per-partition).

## Production Notes

Run an access review specifically for `fraud` and `finance` domain IAM
bindings before go-live, cross-checked against
[`01-discovery/questions/03-security-team.md`](../01-discovery/questions/03-security-team.md)
findings on current Ranger policy granularity — these domains warrant the
tightest scrutiny given their compliance sensitivity.
