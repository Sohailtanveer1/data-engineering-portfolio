# SLA Inventory

**Purpose:** Capture the actual, current, per-job or per-pipeline SLA —
distinguishing documented SLA, business-expected SLA (from
[`questions/05-business.md`](../questions/05-business.md)), and observed
actual performance. These three frequently disagree, and the disagreement
itself is important information.
**Owner:** Migration Program Lead, populated with Data Engineering and
confirmed with Business Owners.
**Inputs:** Job schedules, historical run-time logs, business interviews.
**Outputs:** Feeds [`14-job-migration/`](../../14-job-migration/README.md)
wave prioritization and [`17-performance/`](../../17-performance/README.md)
target benchmarks.
**Prerequisites:** [`06-job-inventory.md`](06-job-inventory.md) started
(SLA inventory is keyed to job IDs from there).
**Validation method:** Compare "Documented SLA" against "Observed P95 actual
duration" pulled from YARN application history / scheduler logs over the
trailing 90 days — a job that "meets SLA" on paper but routinely runs at
95% of its SLA window is a migration risk, not a stable baseline.

---

## SLA inventory table

| Job ID | Job / Pipeline Name | Business Function | Documented SLA (deadline) | Business-Expected SLA (from interview) | Observed P50 Duration | Observed P95 Duration | SLA Breach Frequency (last 90d) | Criticality Tier* |
|---|---|---|---|---|---|---|---|---|
| EX-001 | `pricing_nightly_batch` | Pricing | Complete by 04:00 local | Complete by 03:00 (buffer for merch review) | 1h 40m | 2h 15m | 2 breaches / 90d | Tier 1 |
| EX-002 | `fraud_score_hourly` | Fraud | Complete within 20 min of trigger | Same | 8 min | 14 min | 0 breaches / 90d | Tier 1 |
| EX-003 | `inventory_sync_intraday` | Inventory/Supply Chain | Every 15 min, <10 min lag | Same | 6 min | 9 min | 1 breach / 90d | Tier 1 |
| EX-004 | `marketing_campaign_attribution` | Marketing | Complete by 06:00 | "By start of business, ~08:00 is fine" | 3h 10m | 4h 05m | 5 breaches / 90d | Tier 2 |
| EX-005 | `finance_gl_reconciliation` | Finance | Complete by 05:00 on month-end +1 | Same, hard regulatory deadline | 2h 20m | 2h 55m | 0 breaches / 90d | Tier 1 |

*Rows above are illustrative examples showing the expected shape and level
of detail — replace with the actual inventory captured from this
environment's job scheduler and business interviews. Every row must be
populated, not sampled, before this document is considered complete.

\* Criticality Tier is assigned per
[`02-business-critical-jobs.md`](02-business-critical-jobs.md) — do not
assign it independently in this document; reference the decision made
there.

## What to do with SLA breach patterns

- **Documented SLA met but business-expected SLA missed**: this is a silent
  business dissatisfaction risk — the pipeline "works" on paper but the
  business already doesn't trust it. Flag for priority review in
  [`17-performance/`](../../17-performance/README.md).
- **Frequent breaches (>5% of runs)**: this job is already fragile on-prem.
  Migrating it "as-is" without addressing root cause will likely reproduce
  or worsen the breach pattern on Dataproc. Flag for redesign consideration,
  not just re-platforming.
- **P95 within 10% of SLA deadline**: little margin for error. These jobs
  need the most conservative wave placement and the longest parallel-run
  validation window in [`14-job-migration/`](../../14-job-migration/README.md).

## Common Mistakes

- Recording only the documented SLA and skipping the business-expected SLA
  interview — the two are frequently different, and the business-expected
  one is what actually gets escalated when missed.
- Using average duration instead of P95 — averages hide the tail risk that
  actually causes SLA breaches.

## Production Notes

For ecommerce specifically, re-verify every Tier 1 SLA against **peak
trading day** performance, not just a typical weekday — a job that
comfortably meets SLA on a normal Tuesday may not on Black Friday. Where
peak-day historical data exists, capture it as a separate column extension
to this table.
