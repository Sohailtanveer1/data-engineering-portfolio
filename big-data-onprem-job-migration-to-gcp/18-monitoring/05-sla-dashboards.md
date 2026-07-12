# SLA Dashboards

**Purpose:** Give business stakeholders direct, self-service visibility
into whether their pipelines are meeting SLA — a capability the current
on-prem platform generally lacks (per
[`01-discovery/questions/07-operations.md`](../01-discovery/questions/07-operations.md)
findings on MTTD and business communication).
**Owner:** Platform Engineering, content reviewed with each Business
Owner.

---

## Design principle: business language, not engineering metrics

An SLA dashboard for a Business Owner shows "Was pricing data ready by
3:00 AM as expected? ✅/❌, for the last 30 days" — not raw Dataproc
cluster CPU utilization or YARN queue depth. Translate engineering
metrics into the business-meaningful question each Business Owner
actually cares about, per the SLA inventory
([`01-discovery/inventories/01-sla-inventory.md`](../01-discovery/inventories/01-sla-inventory.md))
business-expected SLA column, not just the documented technical SLA.

## Dashboard content per domain

| Panel | Shows |
|---|---|
| SLA compliance calendar (last 30/90 days) | Green/red per day — was the business-expected deadline met |
| Trend | SLA compliance % over time — improving, stable, or degrading |
| Current status | Today's run status — completed, in progress, delayed |
| Data quality | Validation pass rate per [`16-data-validation/`](../16-data-validation/README.md), in plain language ("Data quality checks: 100% passed this month") |

## Access

SLA dashboards are shared directly with Business Owners (read-only Cloud
Monitoring dashboard access, or embedded/exported into a business-familiar
tool if preferred) — not locked behind an engineering-only tool the
business would need to request access to and learn to use.

## Review cadence

- **Business Owner self-service**: available anytime.
- **Formal review**: monthly during the migration program (feeding
  [`00-project-overview/04-timeline-and-phases.md`](../00-project-overview/04-timeline-and-phases.md)
  status reporting) and quarterly thereafter in steady-state operation.

## Common Mistakes

- Building a technically accurate but practically unreadable dashboard
  for a non-technical audience, causing Business Owners to stop checking
  it and revert to asking engineering directly (defeating the self-service
  purpose).
- Only building this dashboard for Tier 1 domains — Tier 2 domains'
  business owners also benefit from and often explicitly request this
  visibility once they see it exists for Tier 1.

## Production Notes

Walk each Tier 1 Business Owner through their domain's SLA dashboard
directly (not just send a link) before that domain's production cutover —
this is also a natural moment to confirm the dashboard actually reflects
what they consider their real SLA expectation, closing the loop with
[`01-discovery/inventories/01-sla-inventory.md`](../01-discovery/inventories/01-sla-inventory.md).
