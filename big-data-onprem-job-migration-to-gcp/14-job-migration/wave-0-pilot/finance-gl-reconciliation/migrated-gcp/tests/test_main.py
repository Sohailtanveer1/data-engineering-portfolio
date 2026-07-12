"""
Tests for the orchestration entry point, using FakeBigQueryReconciliationClient
— no real BigQuery connection, no JVM. See ../../migration-record.md.
"""

import pytest

from finance_gl_reconciliation.bigquery_runner import FakeBigQueryReconciliationClient
from finance_gl_reconciliation.main import run
from finance_gl_reconciliation.validation import GLBalanceError, ReconciliationRow


def _row(debits=100.0, credits=100.0):
    return ReconciliationRow(
        journal_id="J1",
        account_code="A1",
        fiscal_period="202607",
        total_debits=debits,
        total_credits=credits,
        balance=round(debits - credits, 2),
    )


class TestRun:
    def test_balanced_period_completes_without_error(self):
        client = FakeBigQueryReconciliationClient(fixed_rows=[_row(100.0, 100.0)])
        run(project_id="acme-data-platform-prod", fiscal_period="202607", client=client)
        assert client.merge_called_with == "202607"

    def test_imbalanced_period_raises_and_does_not_swallow_the_error(self):
        client = FakeBigQueryReconciliationClient(fixed_rows=[_row(100.0, 90.0)])
        with pytest.raises(GLBalanceError):
            run(project_id="acme-data-platform-prod", fiscal_period="202607", client=client)

    def test_merge_runs_before_validation_even_when_validation_will_fail(self):
        # The merge must still execute (data lands in BigQuery) even if
        # the subsequent balance check is going to fail the task — we
        # want the imbalance to be visible/queryable for investigation,
        # not silently discarded because validation failed first.
        client = FakeBigQueryReconciliationClient(fixed_rows=[_row(100.0, 50.0)])
        with pytest.raises(GLBalanceError):
            run(project_id="acme-data-platform-prod", fiscal_period="202607", client=client)
        assert client.merge_called_with == "202607"
