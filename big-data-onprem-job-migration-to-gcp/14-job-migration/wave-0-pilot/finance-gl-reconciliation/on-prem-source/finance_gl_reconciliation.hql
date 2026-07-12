-- finance_gl_reconciliation.hql — ON-PREM ORIGINAL (Hive, run via `hive -f`).
--
-- Runs monthly, month-end+1, triggered by an Oozie coordinator (see
-- run_finance_gl_reconciliation.sh). Captured as-is during
-- 02-dependency-analysis/methodology/02-hive-dependencies.md review.
--
-- Known issues (do not fix here — see ../migration-record.md):
--   - No explicit debit=credit balance validation anywhere in this
--     script or its wrapper — an imbalanced journal entry silently
--     flows through to the output table
--   - Hardcoded fiscal_period substitution via shell (see wrapper)
--     instead of a proper Hive parameter
--   - INSERT OVERWRITE on the whole table, not just the target
--     fiscal_period partition — technically idempotent for a full
--     re-run, but wasteful (reprocesses every historical period every
--     month) and risky (a bug in this run can silently corrupt prior,
--     already-closed and audited fiscal periods)

INSERT OVERWRITE TABLE finance.gl_reconciliation_monthly
SELECT
  journal_id,
  account_code,
  fiscal_period,
  SUM(debit_amount)  AS total_debits,
  SUM(credit_amount) AS total_credits,
  SUM(debit_amount) - SUM(credit_amount) AS balance
FROM finance.gl_entries_raw
GROUP BY journal_id, account_code, fiscal_period;
