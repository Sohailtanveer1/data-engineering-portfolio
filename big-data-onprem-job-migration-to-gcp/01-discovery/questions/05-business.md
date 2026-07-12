# Discovery Questions — Business Function Owners

**Purpose:** Technical teams can describe *what* a job does; only the
business owner can describe *why it matters* and *what happens if it's
late or wrong*. This interview is where true business-criticality and real
SLA requirements — as opposed to assumed ones — get captured.
**Owner:** Migration Program Lead, conducted per business function (e.g.,
separately with Merchandising, Finance, Fraud, Marketing, Supply Chain).
**Audience:** Business function owners/directors for each major consumer of
platform data (pricing, inventory, fraud, finance, marketing, merchandising).

---

## Questions

| # | Question | Why we ask it |
|---|---|---|
| 1 | Which reports, dashboards, or data feeds does your team depend on from this platform? | Directly builds the business-side view of [`06-job-inventory.md`](../inventories/06-job-inventory.md) — cross-referenced against the technical inventory to find gaps. |
| 2 | If this data were delayed by 1 hour / 4 hours / 24 hours, what actually happens in your business process? | Turns vague "this is important" into a concrete, defensible SLA and criticality tier for [`02-business-critical-jobs.md`](../inventories/02-business-critical-jobs.md). |
| 3 | If this data were simply wrong (not late, but incorrect) for a day, what's the business impact? | Correctness-sensitivity varies independently from latency-sensitivity — pricing and fraud data are often more correctness-sensitive than latency-sensitive, which changes validation priority in [`16-data-validation/`](../../16-data-validation/README.md). |
| 4 | Are there specific times of month/quarter/year when this data matters more than usual (month-end close, promotional launches, peak season)? | Feeds [`03-peak-hours-and-downtime-windows.md`](../inventories/03-peak-hours-and-downtime-windows.md) and the charter's freeze-window definition. |
| 5 | Who on your team currently gets paged or escalated to if this data doesn't show up? | Confirms real (not org-chart) ownership — feeds contact info in the job inventory. |
| 6 | Are there regulatory or contractual obligations tied to this data being available or accurate (e.g., financial reporting deadlines, partner SLAs)? | These are non-negotiable constraints that must be explicitly protected through the migration, not just "best effort." |
| 7 | Is there a manual workaround your team uses today when this pipeline is late or broken? | Reveals the platform's real failure tolerance — if a manual workaround exists and is well-practiced, the true criticality may be lower than assumed (or the workaround may itself be fragile and worth knowing about). |
| 8 | Do you have any planned changes to how you'll use this data in the next 12 months? | New use cases (e.g., a planned BI migration, a new ML model) may change requirements mid-migration and should be flagged early rather than surfacing as scope creep. |
| 9 | Who else outside your immediate team consumes reports or decisions built on this data? | Surfaces second-order dependencies that the direct data consumer may not think to mention unprompted. |
| 10 | On a scale that matters to you, not to engineering, how would you rank this pipeline against your other 5 most important tools/systems? | Forces a relative priority ranking, which is far more useful for wave sequencing than an absolute "critical/not critical" label everyone inflates. |

## Validation of answers

Cross-check stated criticality against actual historical incident/escalation
records (if a ticketing system exists) — teams sometimes overstate current
criticality for a pipeline that used to matter more than it does today.
