# Logging Architecture

**Purpose:** Define how structured logs from every layer (Spark jobs,
Composer DAGs, Terraform/infrastructure) flow into Cloud Logging in a
consistently queryable, correlated form.
**Owner:** Platform Engineering.

---

## Log sources and ingestion

| Source | Ingestion Method |
|---|---|
| Spark job structured logs (per [`07-spark-migration/06-logging-and-error-handling.md`](../07-spark-migration/06-logging-and-error-handling.md)) | Dataproc automatically forwards job driver/executor logs to Cloud Logging; structured JSON format ensures fields are parsed, not just raw text |
| Composer/Airflow task logs | Native Composer integration with Cloud Logging |
| Terraform apply logs (from [`ci-cd/`](../ci-cd/README.md)) | CI/CD pipeline logs forwarded to Cloud Logging for audit trail |
| Cloud Audit Logs (per [`10-security/05-audit-logging.md`](../10-security/05-audit-logging.md)) | Native, always flowing to Cloud Logging |

## Log correlation

Every log line from a single job execution shares a common `run_id` (per
[`07-spark-migration/06-logging-and-error-handling.md`](../07-spark-migration/06-logging-and-error-handling.md)),
enabling a single Cloud Logging query to pull the complete execution
trace across cluster creation, job submission, transformation steps, and
cluster teardown:

```
resource.type="cloud_dataproc_cluster"
jsonPayload.run_id="pricing-nightly-20260712"
```

## Log-based metrics

Key structured fields are promoted to **log-based metrics** in Cloud
Monitoring, enabling alerting and dashboarding without needing to query
raw logs for common questions (e.g., "count of Terminal/Data errors per
job per day," derived from the `severity` and `error_classification`
fields per
[`07-spark-migration/06-logging-and-error-handling.md`](../07-spark-migration/06-logging-and-error-handling.md)).

## Log retention and export

| Log Category | Cloud Logging Retention | Long-Term Export |
|---|---|---|
| Standard application logs | 30 days (default, sufficient for operational troubleshooting) | Exported to a BigQuery sink for longer-term trend analysis if needed |
| Audit logs (Data Access, Admin Activity) | Extended per compliance requirement, per [`10-security/05-audit-logging.md`](../10-security/05-audit-logging.md) | Exported to an immutable, access-restricted sink |

## Common Mistakes

- Logging unstructured free-text strings as the primary log content
  instead of structured JSON fields, making later querying and alerting
  far harder than necessary.
- Missing the `run_id` correlation field on some log lines (e.g., a log
  statement inside a shared utility function that doesn't have access to
  the calling job's context), fragmenting the execution trace.

## Production Notes

Validate log correlation explicitly for a Tier 1 job's full execution
trace (cluster creation through teardown) before that job's production
cutover — confirm an on-call engineer can actually pull the complete
picture from a single `run_id` query during a real incident, not just in
theory.
