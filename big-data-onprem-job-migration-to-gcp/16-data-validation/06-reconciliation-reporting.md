# Reconciliation Reporting

**Purpose:** Define the standard report format produced by every
validation run, and how it's distributed/reviewed — turning individual
check results into a decision-ready artifact for sign-off gates throughout
[`14-job-migration/`](../14-job-migration/README.md).
**Owner:** Data Engineering.

---

## Report format

Every validation run produces a structured report (stored in a BigQuery
table for queryability and trend analysis, plus a human-readable summary):

```json
{
  "table": "pricing.daily_price_snapshot",
  "run_id": "recon-20260712-0300",
  "run_timestamp": "2026-07-12T03:00:00Z",
  "trigger": "post_job_run",
  "overall_status": "PASS",
  "checks": [
    {"type": "row_count", "status": "PASS", "source_value": 2145892, "target_value": 2145892},
    {"type": "aggregate_sum_base_price", "status": "PASS", "source_value": 48213904.22, "target_value": 48213904.21, "tolerance": 0.01},
    {"type": "null_check", "status": "PASS", "details": "0 unexpected nulls across 3 checked columns"},
    {"type": "duplicate_check", "status": "PASS", "details": "0 duplicates on key (sku, dt)"},
    {"type": "business_rule_discount_cap", "status": "PASS", "details": "0 violations"}
  ]
}
```

## Report distribution

| Audience | What They See |
|---|---|
| Data Engineering (executing team) | Full detailed report, every check |
| Migration Program Lead | Summary roll-up across all tables/jobs, feeding [`14-job-migration/03-migration-tracker.md`](../14-job-migration/03-migration-tracker.md) |
| Business Owner (Tier 1/2) | Plain-language summary: "Validation passed — X records checked, 0 discrepancies" or a clear description of any failure and its resolution status |
| Cloud Monitoring | Pass/fail as a metric, feeding dashboards and alerts per [`18-monitoring/`](../18-monitoring/README.md) |

## Trend reporting

Beyond individual run reports, maintain a **trend view** — validation pass
rate over time, per table — surfacing tables with intermittent or
recurring validation issues that might not warrant an immediate hard
failure on any single run but indicate an underlying, worth-investigating
pattern.

## Report retention

Reconciliation reports for Tier 1 tables are retained per the audit
retention requirement in
[`10-security/05-audit-logging.md`](../10-security/05-audit-logging.md) —
these reports are potential compliance evidence demonstrating the
migration (and ongoing operation) was executed with rigor.

## Common Mistakes

- Producing reports only in a format useful to engineers (raw JSON/logs)
  with no plain-language summary for business stakeholders who need to
  sign off but shouldn't need to parse technical output.
- Discarding historical reports after a table's migration is complete,
  losing the trend-analysis capability and audit trail value.

## Production Notes

For Tier 1 tables, the Business Owner sign-off gate in
[`14-job-migration/07-production-deployment-checklist.md`](../14-job-migration/07-production-deployment-checklist.md)
should reference the actual reconciliation report, not just a verbal
assurance that "validation passed" — make the report itself part of the
sign-off record.
