"""
finance_finance_gl_reconciliation — Cloud Composer DAG.

Replaces finance_gl_coordinator.xml (see ../../on-prem-source/). No
Dataproc cluster anywhere in this DAG — per
../../dependency-analysis.md "migration readiness note", this job
targets BigQuery directly (BigQueryInsertJobOperator for the MERGE, a
PythonOperator for the balance-check gate), a fundamentally different
pattern from pricing_nightly_batch and inventory_sync_intraday.

Also fixes the confirmed year-boundary fiscal_period bug from
run_finance_gl_reconciliation.sh — computed here via Python's
dateutil.relativedelta instead of shell `date -d "last month"`, and
covered by a dedicated unit test (see ../tests/test_fiscal_period.py).
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator

PROJECT_ID = "{{ var.value.gcp_project_id }}"


def compute_fiscal_period(**context) -> str:
    """
    Correctly rolls the prior month across a year boundary — the exact
    bug confirmed in the on-prem shell wrapper
    (../../on-prem-source/run_finance_gl_reconciliation.sh). See
    ../tests/test_fiscal_period.py for the regression test.
    """
    from dateutil.relativedelta import relativedelta

    execution_date = context["logical_date"]
    fiscal_period_date = execution_date - relativedelta(months=1)
    fiscal_period = fiscal_period_date.strftime("%Y%m")
    context["ti"].xcom_push(key="fiscal_period", value=fiscal_period)
    return fiscal_period


def run_balance_check(**context) -> None:
    from finance_gl_reconciliation.bigquery_runner import BigQueryReconciliationClient
    from finance_gl_reconciliation.validation import assert_gl_balances

    fiscal_period = context["ti"].xcom_pull(task_ids="compute_fiscal_period", key="fiscal_period")
    client = BigQueryReconciliationClient(project_id=PROJECT_ID)
    rows = list(client.fetch_reconciliation_rows(fiscal_period))
    assert_gl_balances(rows)  # raises GLBalanceError -> task fails -> alert fires, per design


default_args = {
    "owner": "data-engineering-finance",
    "retries": 1,  # a data-quality failure (imbalance) should NOT be blindly retried —
                   # low retry count is deliberate, per 07-spark-migration/06-logging-and-error-handling.md
                   # Terminal/Data classification
    "retry_delay": timedelta(minutes=15),
    "sla": timedelta(hours=2),
    "start_date": datetime(2026, 1, 1),
    "params": {"tier": 1},
}

with DAG(
    dag_id="finance_finance_gl_reconciliation",
    schedule_interval="0 5 1 * *",  # month-end+1, 05:00 — matches the on-prem coordinator
    default_args=default_args,
    catchup=False,
    tags=["finance", "tier-1", "sox", "wave-0-pilot"],
) as dag:

    compute_period = PythonOperator(
        task_id="compute_fiscal_period",
        python_callable=compute_fiscal_period,
    )

    run_merge = BigQueryInsertJobOperator(
        task_id="run_gl_reconciliation_merge",
        configuration={
            "query": {
                "query": "{% include 'sql/gl_reconciliation.sql' %}",
                "useLegacySql": False,
                "queryParameters": [
                    {
                        "name": "fiscal_period",
                        "parameterType": {"type": "STRING"},
                        "parameterValue": {
                            "value": "{{ ti.xcom_pull(task_ids='compute_fiscal_period', key='fiscal_period') }}"
                        },
                    }
                ],
            }
        },
        project_id=PROJECT_ID,
    )

    check_balance = PythonOperator(
        task_id="run_balance_check",
        python_callable=run_balance_check,
    )

    compute_period >> run_merge >> check_balance
