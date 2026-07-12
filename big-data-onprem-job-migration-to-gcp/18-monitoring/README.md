# 18 — Monitoring & Observability

## Purpose

Build the observability layer that closes the MTTD/MTTR gaps identified in
[`01-discovery/questions/07-operations.md`](../01-discovery/questions/07-operations.md)
— giving operations visibility into platform health that meets or beats
current on-prem tooling, and giving the business SLA visibility it
currently lacks.

## Owner

**Platform Engineering / SRE**, with dashboards co-designed with
Operations (per
[`01-discovery/questions/07-operations.md`](../01-discovery/questions/07-operations.md)).

## Inputs

- Structured logging output from every job (per
  [`07-spark-migration/06-logging-and-error-handling.md`](../07-spark-migration/06-logging-and-error-handling.md)).
- DAG execution metrics from
  [`09-composer-migration/05-monitoring-retries-and-alerts.md`](../09-composer-migration/05-monitoring-retries-and-alerts.md).
- SLA targets from
  [`01-discovery/inventories/01-sla-inventory.md`](../01-discovery/inventories/01-sla-inventory.md).

## Outputs

- Cloud Logging structured log ingestion, queryable and correlated.
- Cloud Monitoring dashboards per data domain and platform-wide.
- Alerting routed correctly per job ownership and criticality.
- SLA dashboards visible to both engineering and business stakeholders.

## Prerequisites

[`13-infrastructure/`](../13-infrastructure/README.md) gated; must be live
**before** the first production wave cuts over, per the phase gate in
[`00-project-overview/04-timeline-and-phases.md`](../00-project-overview/04-timeline-and-phases.md).

## Deliverables

1. Logging architecture.
2. Metrics and dashboards.
3. Alerting strategy.
4. Error reporting.
5. SLA dashboards.
6. On-call and escalation design.

## Risks

Monitoring built as an afterthought after jobs are already migrated
leaves a visibility gap exactly during the highest-risk early-production
period for those jobs — this is why monitoring is gated before the first
wave, not after.

## Rollback

N/A — monitoring is additive observability, not a system with rollback
implications of its own.

## Validation

Every alert must be validated to actually fire and actually reach the
correct on-call channel via a deliberate test, per
[`15-testing/`](../15-testing/README.md) — not assumed to work from
configuration alone.

## Best Practices

Design dashboards around the questions operations and business
stakeholders actually ask (per Discovery interviews), not a generic
"everything GCP provides" dashboard that's technically complete but
practically unusable.

## Lessons Learned

Alert fatigue from overly broad or overly sensitive alerting is a common
failure mode that leads teams to ignore alerts entirely — tune alert
thresholds deliberately, not just "alert on everything possible."

## Common Mistakes

- Building dashboards only for engineering, missing the business-facing
  SLA dashboard need identified in Discovery.
- Routing all alerts to a single channel instead of per-domain, per-tier
  routing.

## Production Notes

SLA dashboards for Tier 1 domains should be reviewed with the actual
Business Owner before go-live to confirm it shows what they actually
care about, not just what's easy to build.

---

## Folder structure

```
18-monitoring/
├── README.md                             This file
├── 01-logging-architecture.md             Cloud Logging structure and correlation
├── 02-metrics-and-dashboards.md           Cloud Monitoring dashboards
├── 03-alerting-strategy.md                Alert design and routing
├── 04-error-reporting.md                  Error Reporting integration
├── 05-sla-dashboards.md                   Business-facing SLA visibility
└── 06-on-call-and-escalation.md           On-call model and escalation path
```
