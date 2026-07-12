#!/bin/bash
# run_finance_gl_reconciliation.sh — ON-PREM ORIGINAL shell wrapper.
#
# Invoked by the Oozie coordinator monthly, month-end+1 at 05:00. Captured
# during 02-dependency-analysis/methodology/04-shell-script-and-cron-dependencies.md
# review.
#
# Known issues: fiscal_period computed via naive shell date math (breaks
# at year boundaries — a real, confirmed bug that required a manual fix
# every January per the Controller's team), and no automated check that
# the job's own output actually balances before considering it done.

set -e

# BUG (confirmed, recurs every January): this does not correctly roll
# fiscal_period from period 12 of one year to period 1 of the next
# without manual intervention — see ../migration-record.md.
FISCAL_PERIOD=$(date -d "last month" +%Y%m)

HIVE_SCRIPT_DIR=/home/svc_finance_etl/jobs/finance_gl_reconciliation
LOG_FILE=/var/log/finance_jobs/gl_reconciliation_${FISCAL_PERIOD}.log

echo "Starting finance_gl_reconciliation for fiscal_period ${FISCAL_PERIOD}" >> "${LOG_FILE}"

hive -f "${HIVE_SCRIPT_DIR}/finance_gl_reconciliation.hql" \
     -hivevar fiscal_period="${FISCAL_PERIOD}" >> "${LOG_FILE}" 2>&1

EXIT_CODE=$?
if [ ${EXIT_CODE} -ne 0 ]; then
  echo "finance_gl_reconciliation FAILED for ${FISCAL_PERIOD}" >> "${LOG_FILE}"
  mail -s "[FAILED] finance_gl_reconciliation ${FISCAL_PERIOD}" finance-data-eng@acme.com < "${LOG_FILE}"
  exit ${EXIT_CODE}
fi

# NOTE: no balance check here at all. The job is considered "successful"
# purely because Hive exited 0 — an imbalanced journal (debits != credits)
# would not fail this script. This is the single highest-severity finding
# from dependency analysis given the SOX relevance of this table.
echo "finance_gl_reconciliation SUCCESS for ${FISCAL_PERIOD}" >> "${LOG_FILE}"
