# Alerting Strategy

**Purpose:** Define alert conditions, severity, and routing — implementing
the alerting integration referenced in
[`09-composer-migration/05-monitoring-retries-and-alerts.md`](../09-composer-migration/05-monitoring-retries-and-alerts.md)
as concrete Cloud Monitoring alert policies.
**Owner:** Platform Engineering.

---

## Alert catalog

| Alert | Condition | Severity | Routes To |
|---|---|---|---|
| Job failure (Terminal error) | Composer task fails after exhausting retries | Critical (Tier 1) / Warning (Tier 2-3) | Domain on-call channel, per job `owner` field |
| SLA miss warning | Task duration approaching (not yet exceeding) SLA threshold | Warning | Domain on-call channel |
| SLA breach | Task duration exceeds SLA threshold | Critical | Domain on-call + Migration Program Lead (during migration program) / Platform on-call (steady state) |
| Data validation failure | [`16-data-validation/`](../16-data-validation/README.md) reconciliation reports a failure | Critical (Tier 1) / Warning (Tier 2-3) | Domain on-call channel |
| Orphaned Dataproc cluster | Cluster running longer than job family's expected max duration | Warning | Platform Engineering |
| Incremental sync lag | Sync lag exceeds threshold per [`05-storage-migration/04-incremental-sync-strategy.md`](../05-storage-migration/04-incremental-sync-strategy.md) | Warning | Platform Engineering |
| Secret rotation failure | Rotation automation fails validation per [`10-security/07-key-rotation.md`](../10-security/07-key-rotation.md) | Critical | Security Engineering |
| Budget threshold | Cost approaches budget alert threshold per [`19-cost-optimization/`](../19-cost-optimization/README.md) | Warning/Critical (tiered) | Platform Engineering + Finance |

## Severity definitions

| Severity | Response Expectation |
|---|---|
| Critical | Immediate on-call response, page/phone alert |
| Warning | Reviewed during business hours, Slack/email notification |
| Info | Logged and visible on dashboard, no active notification |

## Routing design

Alerts route per the DAG `owner` field (per
[`09-composer-migration/04-dag-best-practices.md`](../09-composer-migration/04-dag-best-practices.md))
to the correct domain team's on-call channel — never a single shared
"all alerts" channel, which causes exactly the alert-fatigue and
unclear-ownership problems flagged in
[`00-project-overview/03-raci-matrix.md`](../00-project-overview/03-raci-matrix.md)
escalation design.

## Alert threshold tuning

Thresholds start conservative (looser) during initial production weeks
for a newly-cutover job, then tighten as a realistic baseline is
established — avoiding alert fatigue from an initially-noisy, not-yet-
calibrated threshold while still catching genuine issues.

## Common Mistakes

- Setting every alert to Critical severity, causing alert fatigue that
  desensitizes on-call responders to genuinely critical alerts.
- Not testing that an alert actually reaches its intended channel — a
  correctly-configured alert policy with a broken notification channel
  integration is silently useless.

## Production Notes

Every Tier 1 job's alert configuration must be explicitly tested (trigger
a deliberate test failure, confirm the alert fires and reaches the
correct channel) before that job's production cutover, per
[`14-job-migration/07-production-deployment-checklist.md`](../14-job-migration/07-production-deployment-checklist.md).
