# Error Reporting

**Purpose:** Configure Cloud Error Reporting to automatically aggregate
and group similar errors across jobs, surfacing new or recurring error
patterns without requiring manual log analysis.
**Owner:** Platform Engineering.

---

## Integration

Structured error logs (per
[`07-spark-migration/06-logging-and-error-handling.md`](../07-spark-migration/06-logging-and-error-handling.md)
error classification) that include a stack trace or structured error
payload are automatically picked up by Cloud Error Reporting, which groups
occurrences of the same underlying error together — surfacing "this error
has occurred 47 times across 3 jobs in the last 24 hours" rather than
requiring manual correlation across individual log lines.

## What Error Reporting adds beyond standard logging/alerting

| Capability | Value |
|---|---|
| Automatic error grouping | Distinguishes "one error occurring 47 times" from "47 distinct errors," changing incident response priority |
| New error detection | Surfaces an error type never seen before, which may indicate a new bug introduced by a recent deployment |
| Cross-job error pattern detection | Reveals when the same underlying issue (e.g., a shared library bug) affects multiple jobs, informing the blast-radius assessment referenced throughout [`07-spark-migration/`](../07-spark-migration/README.md) |

## Ensuring errors are captured correctly

For Error Reporting to group errors usefully, exceptions must be logged
with their full stack trace and a consistent format — the shared
structured logger (per
[`07-spark-migration/06-logging-and-error-handling.md`](../07-spark-migration/06-logging-and-error-handling.md))
is responsible for ensuring this consistently, rather than leaving it to
each job's individual exception handling to get right.

## Common Mistakes

- Catching and re-logging exceptions as a plain string message, losing
  the stack trace information Error Reporting needs to group errors
  accurately.
- Not reviewing the Error Reporting dashboard regularly — it's most
  valuable as a proactive tool (catching new error patterns early) not
  just a reactive one.

## Production Notes

Review the Error Reporting dashboard daily during
[`22-hypercare/`](../22-hypercare/README.md) for every newly-cutover
Tier 1 job — this is one of the fastest ways to catch an emerging issue
before it accumulates into a larger incident.
