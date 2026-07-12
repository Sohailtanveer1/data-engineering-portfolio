# Negative Testing

**Purpose:** Confirm every job handles invalid, malformed, missing, or
unexpected input gracefully and correctly — per the error classification
standard in
[`07-spark-migration/06-logging-and-error-handling.md`](../07-spark-migration/06-logging-and-error-handling.md),
failing fast and clearly rather than producing silently incorrect output
or an unhelpful crash.
**Owner:** QA.

---

## Required negative test scenarios per job

| Scenario | Expected Behavior |
|---|---|
| Missing required input partition/file | Job fails clearly with a Terminal/Data classification, alerts fire, no partial/incorrect output produced |
| Empty input (zero rows) | Job handles gracefully — either produces a valid empty output or fails clearly if zero rows is genuinely invalid for that job's business logic, never crashes with an unhandled exception |
| Malformed schema (unexpected column type, missing expected column) | Job fails clearly at read time with a schema validation error, not a confusing downstream failure many transformation steps later |
| Null values in unexpected places (a column assumed non-null contains nulls) | Job either handles per documented business logic (e.g., excludes the row, per confirmed business rule) or fails clearly — never silently propagates an unhandled null into a calculation producing a wrong (not just missing) result |
| Duplicate records in input | Job's transformation logic handles or explicitly rejects duplicates per confirmed business intent, not silently double-counted |
| Extremely skewed data (one key with disproportionate volume) | Job completes without failure (even if slower) — validated jointly with [`17-performance/`](../17-performance/README.md) skew-handling guidance |
| Invalid/missing configuration value | Job fails fast at startup per [`07-spark-migration/05-configuration-management-and-secrets.md`](../07-spark-migration/05-configuration-management-and-secrets.md), never partway through processing |

## Deriving scenarios from business logic review

Negative test scenarios aren't generic — they should be derived from the
actual business rules confirmed during
[`01-discovery/questions/05-business.md`](../01-discovery/questions/05-business.md)
and
[`01-discovery/questions/06-developers.md`](../01-discovery/questions/06-developers.md)
interviews. For example, `apply_discount_cap`'s negative tests
(see
[`07-spark-migration/examples/test_example_pricing_job.py`](../07-spark-migration/examples/test_example_pricing_job.py))
directly encode the confirmed business rule that discounts must never
exceed the configured cap — a negative test here isn't generic "test with
weird input," it's "confirm the specific business guarantee holds under
adversarial input."

## Common Mistakes

- Writing negative tests that only check "the job doesn't crash" without
  checking that the *correct* handling behavior occurred (clean failure
  vs. silent bad output are both "didn't crash" but very different
  outcomes).
- Deriving negative test scenarios generically instead of from the
  specific business rules and known historical data quality issues for
  each job.

## Production Notes

For Tier 1 jobs, negative test scenarios should specifically include any
known historical data quality issue from the on-prem platform (per
[`01-discovery/questions/06-developers.md`](../01-discovery/questions/06-developers.md)
Q7 — "known bugs, workarounds, or don't-touch-this parts of the code") —
confirming the migrated job handles the same real-world messy data at
least as well as the on-prem version did.
