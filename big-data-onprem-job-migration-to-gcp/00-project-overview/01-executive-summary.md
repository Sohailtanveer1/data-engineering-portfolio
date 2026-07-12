# Executive Summary — On-Prem Hadoop to GCP Migration

**Purpose:** Give an executive, sponsor, or new stakeholder a complete
understanding of this program in under five minutes.
**Owner:** Migration Program Lead
**Audience:** Executive sponsor, VP Engineering, VP Data, Finance (cost
approval), Board-level reporting if applicable.

---

## The situation

Our ecommerce data platform runs on an on-premises Hadoop cluster: HDFS for
storage, Spark for processing, Hive as the SQL/warehouse layer, and a mix of
Oozie, Airflow, and cron for scheduling. This platform currently powers:

- Nightly and intraday batch pipelines that feed **order management,
  inventory, pricing, fraud detection, recommendations, and finance
  reporting**.
- Ad-hoc and scheduled analytics used by merchandising, marketing, and
  finance teams.
- Data feeds to downstream systems: the data warehouse layer consumed by BI
  tools, marketing automation platforms, and partner/vendor data exchanges.

This platform has served the business well, but it now carries costs and
risks that the business has decided to resolve by migrating to Google Cloud
Platform:

- **Capacity is capped by physical hardware.** Peak trading events (Black
  Friday, Cyber Monday, flash sales) push the cluster to its limits every
  year, and adding capacity requires a hardware procurement cycle measured
  in months, not hours.
- **Operational burden.** A dedicated team maintains cluster hardware, OS
  patching, Hadoop/Spark/Hive version upgrades, and Kerberos/Ranger security
  infrastructure — work that does not differentiate us from any other
  ecommerce company and that a managed cloud platform absorbs.
- **Cost is largely fixed, not elastic.** We pay for peak capacity
  year-round even though the cluster is significantly underutilized outside
  of trading peaks and nightly batch windows.
- **Hiring and retention risk.** On-prem Hadoop administration skills are an
  increasingly scarce and aging skill set in the market compared to cloud
  data engineering skills.
- **Disaster recovery is weak.** Our current DR posture for the on-prem
  cluster does not meet the RPO/RTO targets the business now requires (see
  [`01-discovery/`](../01-discovery/README.md) for the documented current
  vs. required DR posture).

## The plan

We are migrating the platform to Google Cloud Platform in a **phased,
wave-based approach** — not a single "big bang" cutover. Storage moves to
Cloud Storage (GCS), Spark processing moves to Dataproc (with a path to
BigQuery for suitable analytical workloads), Hive's role is replaced by a
combination of BigQuery and/or Dataproc-managed Hive Metastore depending on
workload, and all scheduling consolidates onto Cloud Composer (managed
Airflow). Security, networking, infrastructure, and CI/CD are rebuilt
cloud-native from the start — not lifted-and-shifted as-is.

Jobs are migrated in **prioritized waves** (see
[`14-job-migration/`](../14-job-migration/README.md)), starting with
lowest-risk, non-business-critical jobs to prove the pattern, and ending
with the highest-value, highest-risk business-critical pipelines once the
pattern is proven and the team has confidence.

## What "done" looks like

- 100% of in-scope Spark, Hive, and scheduled jobs are running on GCP.
- The on-prem cluster is decommissioned (or reduced to an agreed residual
  footprint, per the exit plan).
- All migrated data has passed the reconciliation validation defined in
  [`16-data-validation/`](../16-data-validation/README.md) — no silent data
  loss or corruption.
- SLAs for business-critical jobs are met or improved on GCP relative to
  their current on-prem baseline (see [`01-discovery/`](../01-discovery/README.md)
  for current SLA inventory).
- The platform has passed a full peak-trading-load cycle on GCP with no
  P1/P2 incidents attributable to the migration.

## Investment and return

Detailed cost modeling lives in
[`19-cost-optimization/`](../19-cost-optimization/README.md). At a summary
level, this program trades a fixed, hardware-bound cost structure for a
variable, usage-bound one, with the expectation of:

- Materially reduced cost during off-peak periods (autoscaling clusters,
  spot/preemptible VMs, storage tiering).
- Elastic peak capacity with no procurement lead time.
- Reduced platform operations headcount need (reallocated to
  higher-value data engineering work rather than infrastructure upkeep).

## Key risks the executive sponsor should be aware of

The full risk register lives in
[`07-risk-register-summary.md`](07-risk-register-summary.md) (and in full
detail in [`documentation/`](../documentation/README.md)). The three risks
most likely to affect timeline or budget:

1. **Undiscovered dependencies.** On-prem platforms accumulate years of
   undocumented shell scripts, cron jobs, and tribal-knowledge dependencies.
   [`02-dependency-analysis/`](../02-dependency-analysis/README.md) exists
   specifically to surface these before they cause a production incident.
2. **Peak-season freeze windows compress the execution calendar.** We do not
   cut over business-critical pipelines during peak trading periods (see
   [`02-migration-charter.md`](02-migration-charter.md)), which means the
   timeline has hard dead zones, not just a hard end date.
3. **Data correctness is non-negotiable.** For a finance- and
   fraud-detection-adjacent platform, a data correctness bug is a much worse
   outcome than a delayed timeline. The program is intentionally
   validation-heavy (see [`16-data-validation/`](../16-data-validation/README.md))
   even though that adds calendar time.

## Sponsor ask

Approval of the charter in [`02-migration-charter.md`](02-migration-charter.md),
the budget outlined in [`19-cost-optimization/`](../19-cost-optimization/README.md),
and the change-freeze windows that constrain when business-critical cutovers
can happen.
