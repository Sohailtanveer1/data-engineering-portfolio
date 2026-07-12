"""
Regression test for the confirmed on-prem year-boundary bug in
../../on-prem-source/run_finance_gl_reconciliation.sh (`date -d "last
month"` failing to roll December -> January correctly in that script's
actual on-prem cron/locale environment, per the Controller's team's
confirmed history of manual January corrections).

Tests the fix directly (dateutil.relativedelta), without needing Airflow
installed, by extracting the same month-rollback logic used in
../dag/finance_gl_reconciliation_dag.py's compute_fiscal_period.
"""

from dateutil.relativedelta import relativedelta
import datetime


def compute_fiscal_period(execution_date: datetime.datetime) -> str:
    """Same logic as dag/finance_gl_reconciliation_dag.py::compute_fiscal_period,
    extracted here as a standalone function so it's testable without an
    Airflow context object."""
    fiscal_period_date = execution_date - relativedelta(months=1)
    return fiscal_period_date.strftime("%Y%m")


class TestComputeFiscalPeriod:
    def test_mid_year_rollback(self):
        assert compute_fiscal_period(datetime.datetime(2026, 7, 1)) == "202606"

    def test_year_boundary_january_execution_rolls_to_prior_december(self):
        # This is the exact case the on-prem shell script got wrong.
        assert compute_fiscal_period(datetime.datetime(2026, 1, 1)) == "202512"

    def test_leap_year_february_boundary(self):
        assert compute_fiscal_period(datetime.datetime(2024, 3, 1)) == "202402"

    def test_end_of_month_execution_date_still_rolls_correctly(self):
        # relativedelta handles day-of-month edge cases (e.g. Jan 31 has
        # no direct "one month back" equivalent day) without manual
        # workarounds, unlike naive shell date arithmetic.
        assert compute_fiscal_period(datetime.datetime(2026, 3, 31)) == "202602"
