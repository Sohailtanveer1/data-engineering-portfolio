"""
Pure-Python tests — no PySpark, no BigQuery, no JVM required. Unlike the
other two Wave 0 pilot jobs, these are actually executable in any
standard Python environment, including this one. See ../../migration-record.md.
"""

import pytest

from finance_gl_reconciliation.validation import (
    GLBalanceError,
    ReconciliationRow,
    assert_gl_balances,
    find_imbalanced_journals,
)


def _row(journal_id="J1", account_code="A1", debits=100.0, credits=100.0):
    return ReconciliationRow(
        journal_id=journal_id,
        account_code=account_code,
        fiscal_period="202607",
        total_debits=debits,
        total_credits=credits,
        balance=round(debits - credits, 2),
    )


class TestFindImbalancedJournals:
    def test_balanced_journal_is_not_flagged(self):
        rows = [_row(debits=500.0, credits=500.0)]
        assert find_imbalanced_journals(rows) == []

    def test_imbalanced_journal_is_flagged(self):
        rows = [_row(debits=500.0, credits=480.0)]
        result = find_imbalanced_journals(rows)
        assert len(result) == 1
        assert result[0].balance == 20.0

    def test_multiple_journals_only_imbalanced_ones_flagged(self):
        rows = [
            _row(journal_id="J1", debits=100.0, credits=100.0),
            _row(journal_id="J2", debits=200.0, credits=150.0),
            _row(journal_id="J3", debits=50.0, credits=50.0),
        ]
        result = find_imbalanced_journals(rows)
        assert len(result) == 1
        assert result[0].journal_id == "J2"

    def test_empty_result_set_is_not_an_error(self):
        assert find_imbalanced_journals([]) == []

    def test_negative_balance_is_also_flagged(self):
        # credits exceeding debits is still an imbalance, not "extra
        # credit" to be ignored.
        rows = [_row(debits=100.0, credits=150.0)]
        result = find_imbalanced_journals(rows)
        assert len(result) == 1
        assert result[0].balance == -50.0


class TestAssertGLBalances:
    def test_all_balanced_raises_nothing(self):
        rows = [_row(debits=100.0, credits=100.0), _row(journal_id="J2", debits=50.0, credits=50.0)]
        assert_gl_balances(rows)  # should not raise

    def test_any_imbalance_raises_gl_balance_error(self):
        rows = [_row(debits=100.0, credits=90.0)]
        with pytest.raises(GLBalanceError):
            assert_gl_balances(rows)

    def test_error_message_names_the_specific_imbalanced_journal(self):
        rows = [_row(journal_id="J-BAD", account_code="ACCT-7", debits=100.0, credits=95.0)]
        with pytest.raises(GLBalanceError, match="J-BAD/ACCT-7"):
            assert_gl_balances(rows)

    def test_this_is_the_exact_gap_that_existed_on_prem(self):
        """
        Regression guard: the on-prem original
        (../../on-prem-source/finance_gl_reconciliation.hql +
        run_finance_gl_reconciliation.sh) had NO equivalent of this
        check anywhere — a completely imbalanced journal would have
        been written to the output table and reported as job success.
        This test exists specifically to make sure that gap can never
        silently reopen in the migrated version.
        """
        wildly_imbalanced = [_row(debits=1_000_000.0, credits=1.0)]
        with pytest.raises(GLBalanceError):
            assert_gl_balances(wildly_imbalanced)
