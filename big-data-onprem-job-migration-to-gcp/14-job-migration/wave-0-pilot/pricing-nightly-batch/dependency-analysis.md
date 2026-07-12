# Job Dependency Card — `pricing_nightly_batch`

Filled in using
[`02-dependency-analysis/templates/02-job-dependency-card-template.md`](../../../02-dependency-analysis/templates/02-job-dependency-card-template.md)
against the real on-prem source in
[`on-prem-source/`](on-prem-source/).

**Job Name:** `pricing_nightly_batch`
**Type:** Spark (PySpark, Spark 2.4.8)
**Criticality Tier:** Tier 1 — feeds storefront pricing display, per
[`01-discovery/inventories/02-business-critical-jobs.md`](../../../01-discovery/inventories/02-business-critical-jobs.md)
criterion 1.
**Card completed by:** Migration pilot **Date:** 2026-07-12

---

## Upstream dependencies

| Category | Detail | Source | Confirmed via |
|---|---|---|---|
| Data input | Daily price snapshot | `hdfs://nn01.internal.acme.com:8020/data/pricing/daily_price_snapshot/dt=<date>/` | Static code analysis (`pricing_nightly_batch.py`) |
| Data input | Zone lookup (small, non-partitioned) | `hdfs://.../data/pricing/zone_lookup/` | Static code analysis |
| Data input | Active promotions | `hdfs://.../data/pricing/active_promotions/dt=<date>/` | Static code analysis |
| Config/environment | None externalized — all paths and the 40% discount cap are hardcoded in the script | N/A | Static code analysis |
| Shared library/JAR | **None** — logic is entirely self-contained in one script; the discount-cap logic is independently copy-pasted in at least 2 other jobs per developer interview | N/A | [`01-discovery/questions/06-developers.md`](../../../01-discovery/questions/06-developers.md) |
| External system | None direct — all inputs are already-landed HDFS/Hive data | N/A | Static code analysis |

## Downstream consumers

| Consumer | Type | Criticality | Confirmed via |
|---|---|---|---|
| `pricing.daily_price_snapshot_final` (Hive table) | Data | Tier 1 (feeds below) | Static code analysis |
| Storefront pricing display (via a separate sync job, out of this job's direct scope) | Job | Tier 1 | [`01-discovery/questions/05-business.md`](../../../01-discovery/questions/05-business.md) |
| Merchandising Tableau dashboard | BI | Tier 2 | [`01-discovery/questions/08-data-consumers.md`](../../../01-discovery/questions/08-data-consumers.md) |
| `finance_gl_reconciliation` (reads final prices for revenue reconciliation) | Job | Tier 1 | [`02-dependency-analysis/methodology/09-downstream-consumer-analysis.md`](../../../02-dependency-analysis/methodology/09-downstream-consumer-analysis.md) reverse-index |

## Scheduler / workflow context

- **Triggered by:** Time-based, Oozie coordinator, daily 01:00 America/Chicago
- **Upstream job in the workflow graph:** None explicit in Oozie — an
  **undocumented assumption** that `inventory_sync_intraday`'s last run
  of the prior day has already completed by 01:00. This is a real finding,
  not hypothetical — confirmed with the job's current owner.
- **Downstream job(s):** `finance_gl_reconciliation` (informal — no Oozie
  dependency expressed; the finance team simply schedules their job late
  enough that this one is "usually" done first)
- **Conditional/branching logic:** None

## Technical debt / risk flags

- [x] Hardcoded paths/hostnames/credentials found (all data paths, edge
      node hostname, HDFS namenode hostname)
- [x] Uses deprecated Spark APIs (`SparkContext`/`SQLContext` instead of
      `SparkSession`)
- [x] **Not idempotent** — `mode("append")` duplicates rows on re-run for
      the same date
- [x] No automated retry/alerting beyond a single failure email
- [ ] Depends on NFS mount — no
- [x] Duplicated logic also present in other jobs (the discount-cap
      calculation) — not itself a shared library dependency, but a shared
      **pattern** worth consolidating during migration
- [x] Owner confirmed (Data Engineering — Pricing team), no tribal-
      knowledge risk beyond the undocumented inventory-sync timing
      assumption noted above

**Details on flagged items:** The undocumented 01:00 timing assumption is
the single highest-risk finding — it's exactly the kind of dependency
[`02-dependency-analysis/methodology/05-scheduler-workflow-dependencies.md`](../../../02-dependency-analysis/methodology/05-scheduler-workflow-dependencies.md)
warns about, and it's made explicit (not just replicated) in the migrated
DAG via a `GCSObjectExistsSensor`.

## Validation status

- [x] Confirmed via at least one independent technique (static code
      analysis)
- [x] Confirmed via at least two independent techniques (developer
      interview corroborating the timing assumption and the duplicated-
      logic finding)
- [x] Reviewed with job owner (Pricing Data Engineering)
- [x] Reviewed with downstream consumer (Finance, re: `finance_gl_reconciliation`
      timing dependency)

## Migration readiness note

Ready to migrate. No blocking unresolved dependencies. The undocumented
inventory-sync timing assumption and the finance-job timing assumption
are both addressed explicitly in the migrated design (see
[`migration-record.md`](migration-record.md)) rather than carried forward
as informal conventions.
