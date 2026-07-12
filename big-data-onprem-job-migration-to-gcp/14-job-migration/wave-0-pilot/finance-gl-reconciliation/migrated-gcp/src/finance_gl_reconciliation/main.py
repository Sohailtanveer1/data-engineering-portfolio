"""
finance_gl_reconciliation — MIGRATED GCP version, orchestration entry
point. Invoked as a Composer PythonOperator task (not a Spark job — see
../../dependency-analysis.md "migration readiness note").

Compare against ../../on-prem-source/run_finance_gl_reconciliation.sh +
finance_gl_reconciliation.hql. The MERGE logic moved to
sql/gl_reconciliation.sql; the balance check that never existed on-prem
is now a mandatory, explicit gate before this task reports success.
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Optional

from finance_gl_reconciliation.bigquery_runner import BigQueryReconciliationClient
from finance_gl_reconciliation.validation import assert_gl_balances

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("finance_gl_reconciliation")


def run(project_id: str, fiscal_period: str, client: Optional[object] = None) -> None:
    # `client` is injectable (dependency-injection principle, per
    # 07-spark-migration/08-oop-design-patterns.md) so this function is
    # testable with FakeBigQueryReconciliationClient without ever
    # touching real GCP — see ../tests/test_main.py.
    client = client or BigQueryReconciliationClient(project_id=project_id)

    logger.info("running_gl_merge", extra={"fiscal_period": fiscal_period})
    client.run_merge(fiscal_period)

    logger.info("fetching_reconciliation_rows", extra={"fiscal_period": fiscal_period})
    rows = list(client.fetch_reconciliation_rows(fiscal_period))

    # Mandatory gate — did not exist in the on-prem original at all.
    # Raises GLBalanceError (uncaught, propagates as task failure) if
    # anything is imbalanced, per 16-data-validation/04-business-rule-validation.md.
    assert_gl_balances(rows)

    logger.info("gl_reconciliation_balanced", extra={"fiscal_period": fiscal_period, "row_count": len(rows)})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--fiscal-period", required=True)
    args = parser.parse_args(sys.argv[1:])
    run(project_id=args.project_id, fiscal_period=args.fiscal_period)
