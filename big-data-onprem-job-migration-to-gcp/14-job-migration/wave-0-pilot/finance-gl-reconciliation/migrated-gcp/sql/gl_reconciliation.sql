-- gl_reconciliation.sql — MIGRATED GCP version (BigQuery Standard SQL).
--
-- Compare against ../../on-prem-source/finance_gl_reconciliation.hql.
-- Same aggregation logic; two changes:
--   1. Scoped to the target fiscal_period only (MERGE on that partition),
--      not a full-table INSERT OVERWRITE — closes the "reprocesses every
--      historical period, risks corrupting closed periods" finding in
--      ../migration-record.md.
--   2. fiscal_period is now a bound query parameter (@fiscal_period),
--      never computed by fragile shell date arithmetic — closes the
--      confirmed year-boundary bug.
--
-- Executed via BigQueryInsertJobOperator in ../dag/finance_gl_reconciliation_dag.py.
-- Balance validation (debits == credits) happens AFTER this runs, as a
-- separate, explicit gate — see ../src/finance_gl_reconciliation/validation.py
-- and 16-data-validation/04-business-rule-validation.md.

MERGE `acme-data-platform-prod.finance_prod.gl_reconciliation_monthly` AS target
USING (
  SELECT
    journal_id,
    account_code,
    fiscal_period,
    SUM(debit_amount)  AS total_debits,
    SUM(credit_amount) AS total_credits,
    SUM(debit_amount) - SUM(credit_amount) AS balance
  FROM `acme-data-platform-prod.finance_prod.gl_entries_raw`
  WHERE fiscal_period = @fiscal_period
  GROUP BY journal_id, account_code, fiscal_period
) AS source
ON target.journal_id = source.journal_id
   AND target.account_code = source.account_code
   AND target.fiscal_period = source.fiscal_period
WHEN MATCHED THEN
  UPDATE SET
    total_debits = source.total_debits,
    total_credits = source.total_credits,
    balance = source.balance
WHEN NOT MATCHED THEN
  INSERT (journal_id, account_code, fiscal_period, total_debits, total_credits, balance)
  VALUES (source.journal_id, source.account_code, source.fiscal_period,
          source.total_debits, source.total_credits, source.balance);
