# Post-Cutover Validation

**Purpose:** Confirm the cutover actually succeeded — cutover isn't
"complete" the moment the deployment sequence finishes executing, only
once the migrated job has been observed running correctly in real
production conditions.
**Owner:** Data Engineering (Validation Lead).

---

## Immediate post-cutover checks (within hours)

- [ ] First production run completes successfully within expected
      duration.
- [ ] [`16-data-validation/`](../16-data-validation/README.md)
      reconciliation checks pass against the first production output.
- [ ] No Terminal/Data errors logged (per
      [`07-spark-migration/06-logging-and-error-handling.md`](../07-spark-migration/06-logging-and-error-handling.md)).
- [ ] Downstream consumers confirm they're receiving correct data
      (a direct check with at least one representative consumer, not just
      an assumption).
- [ ] Cost/resource utilization is within the expected range per
      [`12-cluster-design/`](../12-cluster-design/README.md) sizing —
      an unexpected spike could indicate a misconfiguration.

## Short-term post-cutover checks (first few runs, first several days)

- [ ] Job consistently meets SLA across multiple runs, not just the first.
- [ ] No recurring or escalating error pattern in
      [`18-monitoring/04-error-reporting.md`](../18-monitoring/04-error-reporting.md).
- [ ] Continuous validation (per
      [`16-data-validation/07-continuous-validation-in-production.md`](../16-data-validation/07-continuous-validation-in-production.md))
      shows consistent pass rate.
- [ ] Business Owner confirms continued satisfaction after several days
      of real production reliance, not just the initial UAT snapshot.

## Sign-off: cutover formally complete

Cutover is formally marked complete (in
[`14-job-migration/03-migration-tracker.md`](../14-job-migration/03-migration-tracker.md))
only after both the immediate and short-term checks pass — at which point
the job transitions from active cutover monitoring into
[`22-hypercare/`](../22-hypercare/README.md) standard elevated monitoring.

## What triggers rollback consideration during this phase

Any check failing above should trigger evaluation against the rollback
trigger criteria in
[`06-rollback-plan.md`](06-rollback-plan.md) — post-cutover validation
exists specifically to catch an issue during this window, when rollback
is still the fast, clean option, rather than letting a problem run longer
before being noticed.

## Common Mistakes

- Declaring cutover "done" immediately after the deployment sequence
  completes, without waiting to observe actual production behavior across
  multiple runs.
- Only checking technical metrics and skipping the direct downstream
  consumer and Business Owner confirmation — a technically "passing" job
  that the business finds unusable is not actually a successful cutover.

## Production Notes

For Tier 1 jobs, extend the short-term validation window to cover at
least one instance of the job's known highest-complexity scenario (e.g.,
the first month-end close on GCP for finance) before considering cutover
fully, unconditionally successful — not just the first few routine runs.
