# Cluster Policies & Governance

**Purpose:** Define who can create Dataproc clusters, with what
configuration, and how sprawl/drift is prevented — the GCP-native
equivalent of the on-prem YARN queue access control documented in
[`03-current-environment/02-yarn-resource-assessment.md`](../03-current-environment/02-yarn-resource-assessment.md).
**Owner:** Platform Engineering + Security Engineering.

---

## Who can create clusters

| Environment | Who Can Create Clusters | How |
|---|---|---|
| `dev` | Individual engineers | Directly, via `gcloud`/Console, using their own scoped access, for active development/testing only |
| `qa`/`stage` | CI/CD service account only | Automated via [`ci-cd/`](../ci-cd/README.md) test pipelines, not manual creation |
| `prod` | Composer's service account only (per job DAG execution) | Never manual — every `prod` cluster is created by a Composer DAG task per [`07-spark-migration/03-dataproc-submission-patterns.md`](../07-spark-migration/03-dataproc-submission-patterns.md), from a Terraform-defined, version-controlled cluster configuration |

This directly prevents the "manual `spark-submit` from an engineer's
workstation" anti-pattern flagged in
[`07-spark-migration/03-dataproc-submission-patterns.md`](../07-spark-migration/03-dataproc-submission-patterns.md)
from having a cluster-creation equivalent.

## Cluster labeling and cost attribution

Every cluster is created with mandatory labels enabling cost attribution
per [`19-cost-optimization/`](../19-cost-optimization/README.md):

```hcl
labels = {
  data_domain   = "pricing"
  job_family    = "pricing-nightly-batch"
  criticality_tier = "1"
  environment   = "prod"
  managed_by    = "terraform"
}
```

Enforced via an Org Policy or a Terraform module-level validation rule
rejecting cluster creation without these labels — not left to convention
alone, since convention drifts.

## Standard cluster configuration governance

Per-job-family cluster configurations (machine types, autoscaling bounds,
initialization actions) are defined **once**, in the Terraform module
library ([`13-infrastructure/`](../13-infrastructure/README.md)), and any
change to a Tier 1 job family's configuration requires the same review
rigor as any other production infrastructure change (per
[`ci-cd/`](../ci-cd/README.md) pull request review process) — never a
manual, undocumented tweak to a running cluster's configuration.

## Preventing orphaned clusters

Per
[`07-spark-migration/03-dataproc-submission-patterns.md`](../07-spark-migration/03-dataproc-submission-patterns.md),
every ephemeral cluster's teardown step uses `trigger_rule="all_done"`.
As a second layer of defense, a scheduled monitoring check (per
[`18-monitoring/`](../18-monitoring/README.md)) alerts on any Dataproc
cluster running longer than its job family's expected maximum duration —
catching an orphaned cluster that somehow evaded the teardown step, before
it accumulates significant unnecessary cost.

## Common Mistakes

- Allowing broad cluster-creation access in `prod` "for troubleshooting
  convenience," reintroducing the undocumented, person-dependent
  operational pattern the migration is meant to eliminate.
- Skipping the orphaned-cluster monitoring check because "the teardown
  step should always work" — defense in depth exists precisely because
  "should always work" isn't the same guarantee as "does always work."

## Production Notes

Review the orphaned-cluster alert's trigger threshold specifically after
each Tier 1 job family's first few production runs — set it based on
observed real run durations plus a reasonable buffer, not a generic
platform-wide default that might be too loose for a fast job or too tight
for a naturally longer one.
