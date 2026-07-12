"""
Thin BigQuery client interface — abstracted so validation.py's calling
code is testable without a real BigQuery connection, mirroring the
QueryRunner pattern in scripts/reconcile_table.py and the dependency-
injection principle in 07-spark-migration/08-oop-design-patterns.md.
"""

from __future__ import annotations

from typing import Iterable

from finance_gl_reconciliation.validation import ReconciliationRow


class BigQueryReconciliationClient:
    """Real implementation — wraps google-cloud-bigquery. Not imported at
    module load time so unit tests never require the dependency."""

    def __init__(self, project_id: str):
        self._project_id = project_id

    def run_merge(self, fiscal_period: str) -> None:
        from google.cloud import bigquery

        client = bigquery.Client(project=self._project_id)
        with open("sql/gl_reconciliation.sql", "r", encoding="utf-8") as f:
            query = f.read()
        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("fiscal_period", "STRING", fiscal_period)]
        )
        client.query(query, job_config=job_config).result()

    def fetch_reconciliation_rows(self, fiscal_period: str) -> Iterable[ReconciliationRow]:
        from google.cloud import bigquery

        client = bigquery.Client(project=self._project_id)
        query = (
            "SELECT journal_id, account_code, fiscal_period, total_debits, total_credits, balance "
            "FROM `acme-data-platform-prod.finance_prod.gl_reconciliation_monthly` "
            "WHERE fiscal_period = @fiscal_period"
        )
        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("fiscal_period", "STRING", fiscal_period)]
        )
        for row in client.query(query, job_config=job_config).result():
            yield ReconciliationRow(**dict(row))


class FakeBigQueryReconciliationClient:
    """Test double — never touches GCP."""

    def __init__(self, fixed_rows: list[ReconciliationRow]):
        self._fixed_rows = fixed_rows
        self.merge_called_with: str | None = None

    def run_merge(self, fiscal_period: str) -> None:
        self.merge_called_with = fiscal_period

    def fetch_reconciliation_rows(self, fiscal_period: str) -> Iterable[ReconciliationRow]:
        return self._fixed_rows
