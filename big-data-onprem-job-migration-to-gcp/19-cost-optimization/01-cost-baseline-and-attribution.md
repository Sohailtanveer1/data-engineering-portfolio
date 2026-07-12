# Cost Baseline & Attribution

**Purpose:** Establish what the platform costs, per domain, from day one —
the foundation every other document in this folder optimizes against.
**Owner:** Platform Engineering / Cloud-DevOps, reviewed by Finance.

---

## On-prem cost baseline (for comparison)

Before GCP costs can be evaluated as "better," establish the true current
on-prem cost — often harder to pin down than expected, since it spans
hardware amortization, data center space/power, licensing, and
administration headcount:

| Cost Category | On-Prem Annual Cost (estimate) |
|---|---|
| Hardware amortization (cluster nodes, network gear) | _(fill in from Finance/IT asset records)_ |
| Data center space/power/cooling | _(fill in)_ |
| Software licensing (Hadoop distribution, if commercial) | _(fill in)_ |
| Platform administration headcount (fully loaded) | _(fill in)_ |
| **Total** | _(sum)_ |

This baseline is the actual comparison point for the business case in
[`00-project-overview/01-executive-summary.md`](../00-project-overview/01-executive-summary.md)
— not a rough guess, since an inaccurate baseline undermines the
credibility of any GCP cost comparison presented to the Executive Sponsor.

## GCP cost attribution model

Every resource is labeled per
[`13-infrastructure/03-naming-and-tagging-standards.md`](../13-infrastructure/03-naming-and-tagging-standards.md)
with `data_domain`, `criticality_tier`, `environment`, and `cost_center` —
enabling a BigQuery billing export query to break down cost precisely:

```sql
SELECT
  labels.value AS data_domain,
  SUM(cost) AS total_cost
FROM `project.billing_export.gcp_billing_export_v1`,
  UNNEST(labels) AS labels
WHERE labels.key = 'data_domain'
  AND invoice.month = '202607'
GROUP BY data_domain
ORDER BY total_cost DESC;
```

## Cost categories tracked

| Category | What's Included |
|---|---|
| Compute (Dataproc) | Cluster VM cost, both on-demand and preemptible/spot workers |
| Storage (GCS) | Per storage class, per data domain |
| BigQuery | Query cost (on-demand) or slot cost (if flat-rate/reservations used) |
| Composer | Environment cost (largely fixed per environment, not per-job) |
| Network | Egress, NAT, Interconnect/VPN costs |
| Other (Secret Manager, KMS, Monitoring) | Typically small but tracked for completeness |

## Monthly cost review

A monthly cost report is generated and reviewed by Platform Engineering
and Finance, comparing actual spend against:

1. The on-prem baseline (demonstrating the business case).
2. The approved budget (per constraint C6).
3. The prior month (trend).

## Common Mistakes

- Comparing GCP cost only against a partial on-prem baseline (e.g.,
  hardware cost alone, ignoring administration headcount) — this
  overstates GCP's relative savings or understates it, depending on what's
  omitted, and either way undermines the comparison's credibility.
- Attributing cost only at the project level, not the domain level,
  losing the ability to identify which specific team/workload is driving
  cost changes.

## Production Notes

Establish the on-prem baseline and the GCP attribution model **before**
the first production wave cuts over — a cost comparison is far more
credible and useful when the baseline was captured deliberately, not
reconstructed retroactively from incomplete records.
