"""
Balance validation — the check that did NOT exist anywhere in the
on-prem original (see ../../on-prem-source/). Closes the highest-severity
finding from ../../dependency-analysis.md: a job that "succeeds" without
ever confirming debits == credits, for a SOX-relevant table.

Deliberately pure Python (no PySpark, no BigQuery client) — the
reconciliation result set for a single fiscal period is small (thousands,
not billions, of rows), so this validation runs as a lightweight
Composer PythonOperator step after the BigQuery MERGE, not as a Spark
job. This also means it's testable and runnable without a JVM, unlike
the other two Wave 0 pilot jobs — see ../migration-record.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


class GLBalanceError(Exception):
    """Raised when one or more journal entries don't balance. Terminal —
    never retried, per 07-spark-migration/06-logging-and-error-handling.md
    error classification principle applied here even without Spark."""


@dataclass
class ReconciliationRow:
    journal_id: str
    account_code: str
    fiscal_period: str
    total_debits: float
    total_credits: float
    balance: float


def find_imbalanced_journals(
    rows: Iterable[ReconciliationRow], tolerance: float = 0.0
) -> list[ReconciliationRow]:
    """
    Returns every row where debits and credits don't match within
    tolerance. Per 16-data-validation/03-aggregation-validation.md,
    financial aggregate checks use zero tolerance by default — exact
    match to the cent, never loosened without Finance sign-off.
    """
    return [row for row in rows if abs(row.balance) > tolerance]


def assert_gl_balances(rows: Iterable[ReconciliationRow], tolerance: float = 0.0) -> None:
    """Raises GLBalanceError listing every imbalanced journal, or returns
    silently if everything balances."""
    imbalanced = find_imbalanced_journals(rows, tolerance=tolerance)
    if imbalanced:
        detail = ", ".join(
            f"{row.journal_id}/{row.account_code}: balance={row.balance}" for row in imbalanced
        )
        raise GLBalanceError(
            f"{len(imbalanced)} journal/account combination(s) do not balance "
            f"for this fiscal period: {detail}"
        )
