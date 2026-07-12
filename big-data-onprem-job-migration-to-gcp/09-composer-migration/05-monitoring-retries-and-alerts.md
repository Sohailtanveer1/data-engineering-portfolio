# Monitoring, Retries & Alerts

**Purpose:** Standardize operational configuration across every DAG,
directly closing the "no alerting on failure" gaps identified in
[`01-discovery/inventories/10-scheduler-inventory.md`](../01-discovery/inventories/10-scheduler-inventory.md)
and integrating with the broader observability design in
[`18-monitoring/`](../18-monitoring/README.md).
**Owner:** Platform Engineering.

---

## Standard `default_args` retry configuration

```python
default_args = {
    "owner": "data-engineering-pricing",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=30),
    "on_failure_callback": alert_on_task_failure,   # see below
    "sla": timedelta(hours=3),                       # from SLA inventory
}
```

Retry counts and delays are set **per job tier**, not uniformly:

| Tier | Default `retries` | Default `retry_delay` |
|---|---|---|
| Tier 1 | 3 | 5 min, exponential backoff | 
| Tier 2 | 2 | 10 min |
| Tier 3 | 1 | 15 min |

Higher-tier jobs get more retry attempts with shorter initial delay,
reflecting their tighter SLA tolerance — but see
[`07-spark-migration/06-logging-and-error-handling.md`](../07-spark-migration/06-logging-and-error-handling.md)
for the underlying principle that **only Retryable/Transient-classified
errors should actually benefit from retry** — Composer-level retry is a
second layer on top of, not a replacement for, the operation-level error
classification already built into job code.

## Alerting integration

```python
def alert_on_task_failure(context):
    """
    Standard failure callback — every DAG in the platform uses this,
    imported from the shared DAG utilities module (see
    09-composer-migration/06-variables-connections-and-secrets.md for
    where shared DAG code lives).
    """
    task_instance = context["task_instance"]
    send_alert(
        severity="critical" if context["params"].get("tier") == 1 else "warning",
        message=f"Task {task_instance.task_id} in DAG {task_instance.dag_id} failed",
        run_id=context["run_id"],
        log_url=task_instance.log_url,
    )
```

Alerts route to Cloud Monitoring per
[`18-monitoring/`](../18-monitoring/README.md), which fans out to the
correct on-call channel based on the DAG's `owner` field — never a single
shared alert channel that requires manual triage to figure out who should
respond.

## SLA miss handling

Airflow's native `sla` parameter, combined with `sla_miss_callback`,
provides an **early warning** distinct from a hard failure — a task
approaching but not yet past its SLA window triggers a lower-severity
notification, giving on-call a chance to investigate before an actual SLA
breach occurs. This is a proactive capability the current on-prem platform
generally lacks (per
[`01-discovery/questions/07-operations.md`](../01-discovery/questions/07-operations.md)
findings on MTTD).

## Monitoring dashboard integration

Every DAG's execution history, task duration trends, and failure rate are
visible in a standard Cloud Monitoring dashboard (per
[`18-monitoring/`](../18-monitoring/README.md)), built from Composer's
exported metrics — not just Airflow's own UI, which is sufficient for
debugging a specific run but not for the trend/SLA-dashboard view
operations needs.

## Common Mistakes

- Setting identical, generous retry counts for every job regardless of
  tier or error type — this delays failure detection for Tier 1 jobs where
  fast detection matters most.
- Routing all alerts to a single shared channel — this reproduces the
  "everyone sees everything, nobody owns anything" alerting anti-pattern
  that makes on-call response slower, not faster.

## Production Notes

For Tier 1 DAGs, validate the actual end-to-end alerting path (failure →
Cloud Monitoring → on-call notification) with a deliberate test failure in
a non-production environment before that DAG's job goes live — an
alerting configuration that looks correct in code review but doesn't
actually reach anyone is worse than no alerting, since it creates false
confidence.
