# Runbook: Validation Failure Investigation

## Trigger

A "Data validation failure" alert fires, per
[`16-data-validation/06-reconciliation-reporting.md`](../16-data-validation/06-reconciliation-reporting.md).

## Diagnosis

1. Pull the reconciliation report for the failing run — identify exactly
   which check(s) failed (row count, aggregate, null, duplicate, business
   rule).
2. Cross-reference against the failure-handling guidance for that check
   type:
   - Row count mismatch → [`06-data-migration/07-data-reconciliation-framework.md`](../06-data-migration/07-data-reconciliation-framework.md)
   - Duplicate/null → [`16-data-validation/05-duplicate-and-null-detection.md`](../16-data-validation/05-duplicate-and-null-detection.md)
   - Business rule → [`16-data-validation/04-business-rule-validation.md`](../16-data-validation/04-business-rule-validation.md)
3. Confirm whether the source and target were compared at a consistent
   point in time — per
   [`06-data-migration/04-snapshot-strategy.md`](../06-data-migration/04-snapshot-strategy.md),
   a timing mismatch (not a real data issue) is a common false-positive
   cause during an active incremental sync window.

## Resolution

1. If timing-related: re-run validation after confirming sync is current.
2. If a real data issue: trace back to the specific job run and, if
   possible, the specific transformation step (via the Spark UI/logs).
3. Fix and re-validate. For a Tier 1 domain, do not resume normal
   operation until the specific reconciliation check passes cleanly.

## Escalation

Any unresolved Tier 1 validation failure escalates immediately to the
domain's Data Engineering lead and, if the root cause implicates the
shared validation framework itself, to Platform Engineering — see the
"systemic issue" note in
[`documentation/issue-tracker.md`](../documentation/issue-tracker.md).

## After resolution

Log per
[`documentation/issue-tracker.md`](../documentation/issue-tracker.md).
For a business-rule violation found in production (not just migration-
time), also confirm with the Business Owner whether downstream reports
were affected and need correction.
