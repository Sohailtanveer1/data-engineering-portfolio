# Metrics & Dashboards

**Purpose:** Define the Cloud Monitoring dashboards built for this
platform, designed around the actual questions operations and engineering
ask — not a generic template.
**Owner:** Platform Engineering, co-designed with Operations.

---

## Dashboard catalog

| Dashboard | Audience | Key Metrics |
|---|---|---|
| Platform Health Overview | Platform Engineering, Operations | Job success/failure rate (platform-wide), active Dataproc cluster count, Composer scheduler health, orphaned cluster alerts (per [`12-cluster-design/06-cluster-policies-and-governance.md`](../12-cluster-design/06-cluster-policies-and-governance.md)) |
| Per-Domain Dashboard (pricing, fraud, finance, inventory, etc.) | Domain-owning Data Engineering team | Job duration trend, resource utilization, validation pass rate (per [`16-data-validation/`](../16-data-validation/README.md)), cost trend |
| Cost Dashboard | Platform Engineering, Finance | Per-domain cost attribution (per [`19-cost-optimization/`](../19-cost-optimization/README.md) labeling), trend vs. budget |
| SLA Dashboard | Business stakeholders | See [`05-sla-dashboards.md`](05-sla-dashboards.md) |

## Key metrics per job

| Metric | Source |
|---|---|
| Job duration (P50/P95/max) | Composer task duration + Dataproc job duration |
| Success/failure rate | Composer task status |
| Data volume processed | Job-level logged metric (row count, bytes) |
| Cluster startup time | Dataproc cluster creation event timestamps |
| Validation pass/fail | [`16-data-validation/06-reconciliation-reporting.md`](../16-data-validation/06-reconciliation-reporting.md) report status |
| Cost | Billing export, labeled per [`13-infrastructure/03-naming-and-tagging-standards.md`](../13-infrastructure/03-naming-and-tagging-standards.md) |

## Dashboard design principles

1. **Answer a specific question per panel** — not "show all available
   metrics," but "does the platform currently look healthy" (overview),
   "is this specific domain's SLA at risk" (per-domain), "are we on
   budget" (cost).
2. **Trend, not just current state** — every key metric shown with
   historical trend (7/30/90-day), not just a current-value snapshot,
   since trend is what reveals gradual degradation before it becomes an
   incident.
3. **Drill-down capability** — a platform-wide overview panel should link
   directly to the relevant per-domain dashboard for investigation, not
   require manually navigating to find it.

## Common Mistakes

- Building one enormous dashboard with every available metric, making it
  hard to quickly answer "is everything okay" at a glance.
- Building dashboards once during migration and never revisiting them as
  operational needs evolve post-hypercare.

## Production Notes

Review dashboard usefulness explicitly with Operations after the first
month of hypercare (per
[`22-hypercare/`](../22-hypercare/README.md)) — adjust based on what
questions actually came up during real incidents versus what was
anticipated during design.
