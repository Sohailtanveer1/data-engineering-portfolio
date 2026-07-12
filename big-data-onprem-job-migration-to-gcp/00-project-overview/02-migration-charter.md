# Migration Charter

**Purpose:** The single source of truth for what this program will and will
not do. Every phase folder in this repository is scoped against this
document. If a decision conflicts with this charter, the charter wins until
it is formally amended (see change control below).
**Owner:** Migration Program Lead (drafts and maintains); Executive Sponsor
(approves and approves amendments).
**Inputs:** Executive Summary, initial stakeholder conversations, current
platform inventory (informal, pre-`01-discovery`).
**Outputs:** Approved scope boundary that gates every subsequent phase.
**Prerequisites:** Executive sponsorship confirmed; budget line opened.
**Deliverables:** This signed-off document; an amendment log if scope changes.
**Risks:** Scope creep if this document is not enforced; scope
under-definition if it's written too vague to be actionable.
**Rollback:** N/A (this is a planning document, not an executed change).
**Validation:** Signed off by Executive Sponsor, Platform Engineering Lead,
Security Lead, and the business owner of the highest-priority job wave.
**Best Practices:** Keep this document short enough that people actually
read it in full. Push detail into the phase folders it references.
**Lessons Learned:** Migrations that don't write an explicit out-of-scope
list spend months re-litigating scope disputes that a one-page list would
have prevented.
**Common Mistakes:** Treating "everything eventually" as in-scope, which
removes any ability to sequence or prioritize.
**Production Notes:** This charter explicitly encodes ecommerce trading
calendar constraints — see "Change Freeze Windows" below.

---

## Objective

Migrate the company's on-premises Hadoop-based data platform (HDFS, Spark,
Hive, and associated scheduling/orchestration) to Google Cloud Platform,
preserving or improving current data SLAs, without introducing data
correctness regressions, and without disrupting business-critical
ecommerce operations (order processing, inventory, pricing, fraud
detection, and financial reporting pipelines).

## In scope

- All Spark batch and streaming jobs currently running on the on-prem
  cluster, as enumerated by the Spark inventory produced in
  [`01-discovery/`](../01-discovery/README.md).
- All Hive-managed and external tables, their metastore definitions,
  partitioning schemes, and any registered UDFs.
- All scheduled orchestration currently implemented via Oozie, Airflow (if
  already partially adopted on-prem), and cron, migrating to Cloud Composer.
- HDFS-resident data required by in-scope jobs — historical data required
  for reprocessing/backfill windows defined per job, plus all data required
  to satisfy the retention and compliance requirements captured in
  [`01-discovery/`](../01-discovery/README.md).
- Shell scripts and shared internal libraries that in-scope Spark/Hive jobs
  depend on.
- Security model redesign (Kerberos/Ranger-equivalent controls reimplemented
  via IAM, Secret Manager, and KMS).
- Network design connecting GCP to on-prem systems that remain (ERP, POS,
  payment gateway, warehouse management systems) for the duration of the
  migration and beyond, where those integrations persist.
- CI/CD pipeline build-out for the new platform (Terraform, Spark job
  packaging, DAG deployment).
- Monitoring, alerting, and cost management for the new platform.
- Kafka topics and Sqoop-based ingestion jobs, **where present** in the
  current environment (see [`01-discovery/`](../01-discovery/README.md) for
  confirmation of what actually exists in this environment).

## Out of scope

- **Application-layer systems** that produce or consume data from the
  platform (ERP, OMS, WMS, POS, payment gateway) — these are data sources
  and sinks, not migration targets. Their integration *points* are in scope;
  the systems themselves are not.
- **BI/reporting tool migration** (e.g., a Tableau/Looker/Power BI upgrade)
  unless directly required by a data platform change (e.g., a connector
  change from Hive to BigQuery). Tracked as a dependency, not a deliverable.
- **Real-time/OLTP databases** not currently integrated with the Hadoop
  platform.
- **Non-data infrastructure** (corporate IT, general application hosting)
  unrelated to the data platform.
- **New feature development.** This is a migration, not a modernization
  redesign of business logic. Jobs are migrated with equivalent behavior
  first; optimization and redesign are explicitly deferred to
  post-hypercare backlog unless required to make the migration itself work
  (e.g., a Spark 2 → Spark 3 deprecated API fix is in scope; a full pipeline
  redesign is not, see [`07-spark-migration/`](../07-spark-migration/README.md)).

If ambiguity arises about whether something is in scope, it is raised to the
Migration Program Lead and resolved via the RACI in
[`03-raci-matrix.md`](03-raci-matrix.md), then logged in the amendment log
below.

## Success criteria

1. **Functional parity** — every in-scope job produces equivalent output on
   GCP as it did on-prem, validated per
   [`16-data-validation/`](../16-data-validation/README.md).
2. **SLA parity or improvement** — no in-scope business-critical job's
   completion time regresses beyond its documented SLA
   (see [`01-discovery/`](../01-discovery/README.md)).
3. **Zero unplanned data loss** — every migrated dataset reconciles against
   its on-prem source per the validation framework.
4. **Security parity or improvement** — access controls on GCP are at least
   as restrictive as on-prem Kerberos/Ranger controls, formally reviewed by
   the security team (see [`10-security/`](../10-security/README.md)).
5. **Cost within approved budget envelope**, tracked in
   [`19-cost-optimization/`](../19-cost-optimization/README.md).
6. **On-prem cluster decommissioned** (or reduced to the explicitly agreed
   residual footprint) by the program end date.
7. **Successful peak-trading cycle** on GCP with no P1/P2 incidents
   attributable to the migration.

## Change freeze windows

Business-critical job cutovers (see wave prioritization in
[`14-job-migration/`](../14-job-migration/README.md)) **will not** be
scheduled during:

- **Black Friday through Cyber Monday** (the full week), plus a 2-week
  stabilization buffer on either side.
- **December 15 – January 2** (peak holiday fulfillment + returns period).
- Any company-declared major promotional event communicated by
  Merchandising/Marketing with at least 4 weeks' notice.
- The final 5 business days of each fiscal quarter (finance close).

Non-business-critical, low-risk jobs may still be migrated during these
windows at the Migration Program Lead's discretion, but no cutover that
could plausibly affect checkout, inventory, pricing, or fraud detection is
permitted in these windows without explicit sign-off from the Executive
Sponsor and the business owner of the affected function.

## Amendment log

| Date | Change | Approved by |
|---|---|---|
| _(none yet — this is the initial charter)_ | | |

Amendments to scope must be logged here with the approving party. An
amendment to this charter that changes cost or timeline materially requires
Executive Sponsor re-approval, not just Program Lead sign-off.
