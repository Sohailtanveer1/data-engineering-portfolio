# Support Guide

**Purpose:** For standing Operations staff supporting the platform after
hypercare handover — where to look, what's normal, and how to respond.
**Audience:** Operations / support staff, post-[`22-hypercare/`](../22-hypercare/README.md)
handover.

---

## Where to look when something seems wrong

1. **Dashboards first** — per
   [`18-monitoring/02-metrics-and-dashboards.md`](../18-monitoring/02-metrics-and-dashboards.md),
   start with the Platform Health Overview, then the specific domain
   dashboard.
2. **Logs** — per
   [`18-monitoring/01-logging-architecture.md`](../18-monitoring/01-logging-architecture.md),
   query by `run_id` to get the full execution trace for a specific job
   run.
3. **Runbooks** — per
   [`runbooks/`](../runbooks/README.md), find the runbook matching the
   symptom.

## Common scenarios

| Symptom | Likely Cause | Where to Look |
|---|---|---|
| Job failed | Check error classification per [`07-spark-migration/06-logging-and-error-handling.md`](../07-spark-migration/06-logging-and-error-handling.md) — Terminal/Data errors need data investigation, Terminal/Configuration errors need a config fix | [`runbooks/`](../runbooks/README.md) job failure runbook |
| Job running late | Check [`18-monitoring/05-sla-dashboards.md`](../18-monitoring/05-sla-dashboards.md) for SLA-miss warning history; check cluster autoscaling behavior | Domain dashboard |
| Data looks wrong | Check [`16-data-validation/06-reconciliation-reporting.md`](../16-data-validation/06-reconciliation-reporting.md) for the most recent validation report | Validation reports, BigQuery `_migration_control` tables |
| Unexpected cost spike | Check for an orphaned cluster per [`12-cluster-design/06-cluster-policies-and-governance.md`](../12-cluster-design/06-cluster-policies-and-governance.md) | Cost dashboard, orphaned cluster alert |

## Escalation

Per
[`18-monitoring/06-on-call-and-escalation.md`](../18-monitoring/06-on-call-and-escalation.md)
— domain on-call first, then platform on-call, then team lead.

## What NOT to do

- Do not manually modify infrastructure "to fix it quickly" — every
  change goes through Terraform per constraint C5
  ([`00-project-overview/06-assumptions-and-constraints.md`](../00-project-overview/06-assumptions-and-constraints.md)),
  even during an incident (use the expedited change process in
  [`13-infrastructure/05-environment-promotion.md`](../13-infrastructure/05-environment-promotion.md)
  instead).
- Do not manually re-run a job without understanding why it failed first
  — a non-idempotent retry of a job with a real bug can make things worse,
  not better (though per
  [`07-spark-migration/07-idempotency-design.md`](../07-spark-migration/07-idempotency-design.md)
  every migrated job should be safely re-runnable — if a retry seems
  unsafe, that itself is worth flagging).

## Keeping this guide current

If you resolve an issue with no existing runbook, write one — per the
hypercare principle in
[`22-hypercare/04-support-runbook-index.md`](../22-hypercare/04-support-runbook-index.md),
this guide and [`runbooks/`](../runbooks/README.md) should keep growing
based on real operational experience.
