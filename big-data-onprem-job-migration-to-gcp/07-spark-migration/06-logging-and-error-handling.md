# Logging, Error Handling & Retry Logic

**Purpose:** Standardize structured logging and error-handling behavior
across every migrated job, replacing the inconsistent, often-silent
failure handling found in
[`01-discovery/questions/07-operations.md`](../01-discovery/questions/07-operations.md)
findings (jobs requiring manual restart as "normal" operation, silent
failures with no alerting).
**Owner:** Platform Engineering.

---

## Structured logging standard

Every job uses the shared library's structured logger, emitting JSON logs
compatible with Cloud Logging's structured log ingestion:

```python
from dp_spark_common.logging.structured_logger import get_logger

logger = get_logger(job_name="pricing_nightly_batch", run_id=run_id)
logger.info("job_started", extra={"run_date": run_date, "input_partition_count": count})
```

Every log line includes, at minimum: `job_name`, `run_id` (correlating all
log lines from a single execution), `timestamp`, `severity`, and a
structured `message` — never an unstructured free-text string as the sole
content, so Cloud Logging queries in
[`18-monitoring/`](../18-monitoring/README.md) can filter and alert
reliably.

## Error classification

Every exception handled in job code is classified as one of:

| Classification | Definition | Handling |
|---|---|---|
| **Retryable/Transient** | Network blip, GCS 429/503, temporary resource unavailability, YARN preemption on a shared cluster | Retry with exponential backoff, per the retry decorator pattern below |
| **Terminal/Data** | Schema mismatch, missing required partition, data validation failure | Fail immediately, do not retry (retrying a data problem wastes time and can mask the real issue), alert on-call per [`18-monitoring/`](../18-monitoring/README.md) |
| **Terminal/Configuration** | Missing required config value, invalid credential | Fail immediately at startup (per the fail-fast principle in [`05-configuration-management-and-secrets.md`](05-configuration-management-and-secrets.md)) |
| **Unknown/Unclassified** | Any exception not matching the above | Treated as Terminal by default (never silently retried) — an explicit classification must be added once the failure mode is understood, rather than leaving it in this bucket long-term |

This explicit classification is the direct fix for pain point #7 (manual,
undocumented operational interventions) — a job that today requires a
human to look at an error and decide "just re-run it" should instead
programmatically know whether a retry is appropriate.

## Retry logic pattern

See [`examples/retry_decorator.py`](examples/retry_decorator.py) for the
full implementation.

```python
from dp_spark_common.retry.decorator import retryable

@retryable(max_attempts=3, backoff_base_seconds=10, retryable_exceptions=(GCSTransientError,))
def read_source_partition(path: str):
    ...
```

Retry logic is applied at the **operation level** (a specific read/write
call), not blindly around the entire job — retrying an entire multi-hour
job from scratch because of one transient GCS error at the end wastes far
more time than retrying just the failed operation.

## Alerting integration

Every Terminal-classified error triggers a Cloud Monitoring alert per
[`18-monitoring/`](../18-monitoring/README.md), routed to the owning
team's on-call channel — this directly closes the "no alerting on failure"
gap found for several jobs in
[`01-discovery/inventories/10-scheduler-inventory.md`](../01-discovery/inventories/10-scheduler-inventory.md).

## Composer-level retry configuration

In addition to operation-level retries within job code, Composer task-level
retries (`retries`, `retry_delay` on the DAG task) provide a second,
coarser layer of resilience for the overall job submission step (e.g., a
transient Dataproc API error during cluster creation) — see
[`09-composer-migration/`](../09-composer-migration/README.md) for DAG-level
retry configuration standards.

## Common Mistakes

- Wrapping an entire job in a single broad `try/except` that swallows and
  logs any error as a generic failure — this destroys the classification
  information needed for both automated retry decisions and human
  incident triage.
- Configuring unlimited or very high retry counts for Terminal-classified
  errors "just in case" — this delays failure detection and alerting,
  making the on-call response slower, not more resilient.

## Production Notes

For Tier 1 jobs, retry and alerting behavior must be explicitly tested via
fault injection (per
[`15-testing/`](../15-testing/README.md) chaos testing) — simulate a
transient GCS error and confirm the retry logic actually recovers, and
simulate a data/schema error and confirm it fails fast with a clear alert
rather than retrying uselessly.
