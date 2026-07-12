# Migration Record — `finance_gl_reconciliation`

---

## Summary

`finance_gl_reconciliation` (Tier 1, SOX-relevant) migrated from
on-prem Hive+shell (Oozie, monthly) directly to BigQuery — the third
Wave 0 pilot job, and the first with **no Spark/Dataproc involved at
all**, per the per-table warehouse decision framework in
[`04-target-architecture/05-data-warehouse-architecture.md`](../../../04-target-architecture/05-data-warehouse-architecture.md).
This job's tests are the only ones in the pilot that were **actually
executed** in this authoring environment — 16/16 passing — since the
validation logic is pure Python with no JVM dependency.

## What changed, and why

| Issue Found (on-prem) | Fix (GCP) | Reference |
|---|---|---|
| **No debit=credit balance validation anywhere** — a completely imbalanced journal would be written to the output table and the job would still report success | Mandatory `assert_gl_balances` gate after every MERGE, raising and failing the task on any imbalance | [`16-data-validation/04-business-rule-validation.md`](../../../16-data-validation/04-business-rule-validation.md) — **verified with an actual passing test proving this specific gap is closed** (`test_this_is_the_exact_gap_that_existed_on_prem`) |
| **Confirmed year-boundary bug** in `fiscal_period` shell date arithmetic, manually corrected every January for years | Replaced with `dateutil.relativedelta`, covered by 4 tests including the exact January-rollover case | [`test_fiscal_period.py`](migrated-gcp/tests/test_fiscal_period.py) — **verified passing** |
| Full-table `INSERT OVERWRITE` every run, reprocessing and rewriting every historical (already-audited) fiscal period | `MERGE` scoped to `WHERE fiscal_period = @fiscal_period` only — closed periods are never touched by a later run | [`migrated-gcp/sql/gl_reconciliation.sql`](migrated-gcp/sql/gl_reconciliation.sql) |
| No Dataproc/Spark needed — pure aggregation query | BigQuery `MERGE`, orchestrated by `BigQueryInsertJobOperator` — no cluster to provision, size, or tear down for this job at all | [`04-target-architecture/05-data-warehouse-architecture.md`](../../../04-target-architecture/05-data-warehouse-architecture.md) |
| Single failure email, no distinction between "job crashed" and "data is wrong" | Composer task failure (low retry count — 1 — since a data-quality failure should not blindly retry) + alert routed to finance on-call | [`07-spark-migration/06-logging-and-error-handling.md`](../../../07-spark-migration/06-logging-and-error-handling.md) error classification, applied even without Spark |

## What did NOT change

The core aggregation (`SUM(debit_amount)`, `SUM(credit_amount)`, grouped
by `journal_id, account_code, fiscal_period`) is identical logic —
verified by direct comparison between
[`on-prem-source/finance_gl_reconciliation.hql`](on-prem-source/finance_gl_reconciliation.hql)
and
[`migrated-gcp/sql/gl_reconciliation.sql`](migrated-gcp/sql/gl_reconciliation.sql).

## Validation status

| Gate | Status |
|---|---|
| Unit tests written | ✅ 16 tests across `test_validation.py`, `test_main.py`, `test_fiscal_period.py` |
| Unit tests **executed** | ✅ **16/16 passed** — actually run in this environment, no JVM required for this job |
| SQL logic reviewed against on-prem HQL | ✅ Manual side-by-side comparison, same aggregation |
| Integration test against real BigQuery | Not started — requires a real GCP project |
| Parallel-run | Not started — requires the on-prem job and this migrated job running side by side for at least one real fiscal-period close |
| UAT sign-off | Not started — requires Controller review per [`20-uat/`](../../../20-uat/README.md), especially given SOX relevance |

## Next steps

Unlike the other two Wave 0 pilot jobs, the code-level validation here is
already genuinely complete, not just "expected to pass." Remaining work
is entirely about connecting to real infrastructure:

1. Deploy `sql/gl_reconciliation.sql` and the DAG to a real `qa` BigQuery
   dataset.
2. Run the merge against a seeded, intentionally-imbalanced test dataset
   and confirm the task actually fails in the real Composer environment
   (not just in the unit test) — closing the loop per
   [`15-testing/04-end-to-end-testing.md`](../../../15-testing/04-end-to-end-testing.md).
3. Parallel-run against one real fiscal-period close, with the
   Controller directly reviewing output per
   [`20-uat/02-uat-execution-checklist.md`](../../../20-uat/02-uat-execution-checklist.md).
