# Runbook: Job Failure Diagnosis

## Trigger

A "Job failure" alert fires per
[`18-monitoring/03-alerting-strategy.md`](../18-monitoring/03-alerting-strategy.md).

## Diagnosis

1. Open the domain dashboard per
   [`18-monitoring/02-metrics-and-dashboards.md`](../18-monitoring/02-metrics-and-dashboards.md)
   and confirm which job/task failed and its `run_id`.
2. Query Cloud Logging for the full execution trace:
   ```
   jsonPayload.run_id="<run_id>"
   ```
3. Identify the error classification per
   [`07-spark-migration/06-logging-and-error-handling.md`](../07-spark-migration/06-logging-and-error-handling.md):
   - **Retryable/Transient**: Did retries actually engage? Check retry
     count in the logs.
   - **Terminal/Data**: A data issue — missing partition, schema mismatch,
     validation failure.
   - **Terminal/Configuration**: A missing/invalid config value.
4. Check Cloud Error Reporting per
   [`18-monitoring/04-error-reporting.md`](../18-monitoring/04-error-reporting.md)
   to see if this is a new error or a recurring, already-known one.

## Resolution

| Classification | Action |
|---|---|
| Retryable/Transient, retries exhausted | Check the upstream dependency (GCS, Secret Manager, network) for a genuine outage; re-run manually once resolved (job is idempotent per [`07-spark-migration/07-idempotency-design.md`](../07-spark-migration/07-idempotency-design.md), safe to re-run) |
| Terminal/Data | Investigate the specific data issue — missing upstream partition (check the upstream job's status), schema drift (check source system for a recent change), validation failure (see [`validation-failure-investigation-runbook.md`](validation-failure-investigation-runbook.md)) |
| Terminal/Configuration | Check recent changes to Composer Variables/Secret Manager for this job; fix the configuration and re-run |
| Recurring/known error (per Error Reporting) | Check if a fix is already in progress; if not, this may need escalation to Platform Engineering for a code fix |

## Escalation

If root cause isn't clear within 30 minutes for a Tier 1 job, escalate per
[`18-monitoring/06-on-call-and-escalation.md`](../18-monitoring/06-on-call-and-escalation.md).

## After resolution

Log the issue per
[`documentation/issue-tracker.md`](../documentation/issue-tracker.md). If
no runbook covered this scenario, update this runbook or add a new one.
