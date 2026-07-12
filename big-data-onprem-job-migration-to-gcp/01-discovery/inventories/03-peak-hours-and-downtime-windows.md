# Peak Hours & Downtime Windows Inventory

**Purpose:** Document exactly when the platform is under its heaviest load
and when it has genuine slack — both are required to schedule migration
activity (data sync windows, parallel runs, cutovers) without competing
with production load or violating the charter's freeze windows.
**Owner:** Migration Program Lead, populated with Platform Engineering
(technical load data) and Business (trading calendar).
**Inputs:** [`questions/02-platform-team.md`](../questions/02-platform-team.md),
[`questions/05-business.md`](../questions/05-business.md), cluster
utilization telemetry.
**Outputs:** Feeds freeze windows in
[`00-project-overview/02-migration-charter.md`](../../00-project-overview/02-migration-charter.md)
and cutover scheduling in [`21-cutover/`](../../21-cutover/README.md).
**Validation method:** Cross-check business-declared peak periods against
actual historical YARN/cluster utilization metrics for the same dates —
they usually correlate, but confirming this catches surprises (e.g., a
"peak" batch load window that's actually driven by an unrelated internal
reporting deadline, not customer traffic).

---

## Daily / weekly technical load pattern

| Time window (local) | Cluster load level | What's running | Safe for migration activity? |
|---|---|---|---|
| 00:00 – 04:00 | Peak (nightly batch) | Nightly ETL, pricing batch, finance reconciliation | No — reserved for production batch |
| 04:00 – 08:00 | Moderate | Downstream report generation, BI refresh | Limited — non-disruptive validation only |
| 08:00 – 18:00 | Low–moderate (ad-hoc/intraday) | Ad-hoc queries, intraday inventory sync, fraud scoring | Yes, with care — avoid resource-heavy migration jobs during business hours |
| 18:00 – 00:00 | Low | Minimal scheduled load | Best window for migration-related heavy lifting (bulk DistCp, validation runs) |

_(Replace with actual measured utilization from this environment — the
above is an illustrative shape only.)_

## Ecommerce trading calendar — business-declared peak periods

| Period | Dates (recurring) | Why it's peak | Freeze status |
|---|---|---|---|
| Black Friday / Cyber Monday | Late Nov (5-day window) | Highest traffic and order volume of the year | Hard freeze, ±2 weeks buffer |
| Holiday fulfillment & returns | Dec 15 – Jan 2 | Sustained elevated order and returns volume | Hard freeze |
| Quarter-end finance close | Last 5 business days of each fiscal quarter | Finance reconciliation jobs under regulatory deadline | Hard freeze for finance-adjacent jobs |
| Major promotional events | Ad-hoc, per Marketing calendar | Traffic spikes correlated with specific campaigns | Freeze declared per-event, min. 4 weeks notice required |
| Back-to-school / seasonal sales | Varies by category | Elevated but lower than BFCM | Soft freeze — case-by-case Program Lead approval |

## Recurring maintenance / downtime windows (current on-prem)

| Window | Frequency | What happens | Carries forward to GCP? |
|---|---|---|---|
| _(e.g., Sunday 02:00–04:00)_ | Weekly | Cluster maintenance, patching | To be replaced by rolling Dataproc cluster recreation — no equivalent downtime window needed on GCP if ephemeral clusters are used (see [`12-cluster-design/`](../../12-cluster-design/README.md)) |

_(Populate with actual current on-prem scheduled downtime; then explicitly
note in [`04-target-architecture/`](../../04-target-architecture/README.md)
whether GCP eliminates the need for it.)_

## How this feeds the charter

The "Business-declared peak periods" table above is the direct source for
the Change Freeze Windows section of
[`00-project-overview/02-migration-charter.md`](../../00-project-overview/02-migration-charter.md).
If this inventory changes (e.g., a new promotional calendar is announced),
the charter must be updated in the same change.

## Common Mistakes

- Only capturing the "big two" freeze events (BFCM, holidays) and missing
  smaller but still-material recurring peaks (regional sale days, marketplace-specific
  events) that individual business units know about but don't broadcast
  company-wide.
- Assuming low overall cluster utilization means safe migration windows
  everywhere — some Tier 1 jobs run at off-peak-for-the-cluster times that
  are still business-critical (e.g., overnight finance batch).

## Production Notes

Confirm this calendar with Merchandising/Marketing **and** Finance
separately — they track different peak calendars (trading peaks vs.
reporting deadlines) that don't always overlap.
