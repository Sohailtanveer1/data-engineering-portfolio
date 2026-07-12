# Job Dependency Card — `finance_gl_reconciliation`

Filled in using
[`02-dependency-analysis/templates/02-job-dependency-card-template.md`](../../../02-dependency-analysis/templates/02-job-dependency-card-template.md)
against the real on-prem source in
[`on-prem-source/`](on-prem-source/).

**Job Name:** `finance_gl_reconciliation`
**Type:** Hive + Shell (no Spark)
**Criticality Tier:** Tier 1 — SOX-relevant, hard regulatory close
deadline, per
[`01-discovery/inventories/02-business-critical-jobs.md`](../../../01-discovery/inventories/02-business-critical-jobs.md)
criterion 3.
**Card completed by:** Migration pilot **Date:** 2026-07-12

---

## Upstream dependencies

| Category | Detail | Source | Confirmed via |
|---|---|---|---|
| Data input | Raw GL entries (all fiscal periods, full table scan every run) | `finance.gl_entries_raw` (Hive) | Static analysis of `.hql` |
| Config/environment | `fiscal_period` computed via shell date arithmetic, not passed explicitly | `run_finance_gl_reconciliation.sh` | Static code analysis |
| Shared library/JAR | None | N/A | N/A |
| External system | None direct — GL entries land via a separate finance ingestion job, out of this job's scope | N/A | [`01-discovery/inventories/07-application-inventory.md`](../../../01-discovery/inventories/07-application-inventory.md) |

## Downstream consumers

| Consumer | Type | Criticality | Confirmed via |
|---|---|---|---|
| `finance.gl_reconciliation_monthly` (Hive table) | Data | Tier 1 | Static code analysis |
| Finance monthly close reporting (manual, Controller's team) | Business process | Tier 1, SOX-relevant | [`01-discovery/questions/05-business.md`](../../../01-discovery/questions/05-business.md) |
| `pricing_nightly_batch`'s output is read by this job's upstream ingestion — informal, one-directional | N/A | — | Noted for completeness, not a direct dependency of this job itself |

## Scheduler / workflow context

- **Triggered by:** Time-based, Oozie coordinator, monthly, month-end+1
  at 05:00.
- **Confirmed real bug**: the shell wrapper's `fiscal_period` calculation
  (`date -d "last month" +%Y%m`) does not correctly roll from December to
  January across a year boundary in this specific script's implementation
  — the Controller's team has manually corrected this every January for
  several years. This is a genuine, confirmed on-prem defect, not a
  migration-introduced one.
- **Downstream job(s):** None automated — the Controller's team manually
  reviews the output table before it's used in close reporting.
- **Conditional/branching logic:** None in Oozie; the balance-check logic
  that *should* exist as a gate does not exist at all on-prem.

## Technical debt / risk flags

- [x] Hardcoded values (implicit fiscal_period path, no config file)
- [ ] Deprecated Spark APIs — N/A, no Spark involved
- [x] **No idempotency concern in the traditional sense** (full
      `INSERT OVERWRITE` every run is technically idempotent for a given
      run), but re-running the full table on every monthly execution
      needlessly reprocesses and re-writes every historical, already-
      audited fiscal period — a real risk, not just an efficiency concern,
      since a bug in one run can silently corrupt prior closed periods
- [x] **No automated retry/alerting on data quality** — job "succeeds"
      (exit 0) even if output is completely imbalanced
- [x] **Confirmed real bug**: fiscal-period year-boundary calculation
- [ ] Depends on NFS mount — no

**Details on flagged items:** The missing balance validation is the
single highest-priority finding given this table's SOX relevance — see
[`migration-record.md`](migration-record.md) for how it's closed.

## Validation status

- [x] Confirmed via static code analysis (`.hql` + shell wrapper)
- [x] Confirmed via a second technique (Controller's team interview
      corroborating the January bug and the manual-review-only safety net)
- [x] Reviewed with job owner (Finance Data Engineering) and business
      owner (Controller)

## Migration readiness note

Ready to migrate. Per
[`04-target-architecture/05-data-warehouse-architecture.md`](../../../04-target-architecture/05-data-warehouse-architecture.md),
this table targets **BigQuery directly** — no Dataproc/Spark cluster is
needed at all, since the transformation is a pure aggregation query well
suited to BigQuery's engine and this job has no Spark-specific processing
requirement. This is a genuinely different migration pattern from the
other two Wave 0 pilot jobs.
