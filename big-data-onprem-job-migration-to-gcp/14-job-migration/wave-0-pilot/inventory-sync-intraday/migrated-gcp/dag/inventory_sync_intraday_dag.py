"""
inventory_inventory_sync_intraday — Cloud Composer DAG.

Replaces the crontab entry + run_inventory_sync.sh (see
../../on-prem-source/) — no Oozie involved on either side.

TOPOLOGY DECISION (see 12-cluster-design/01-cluster-topology-decision.md
"deciding the intraday-frequency edge case"): at a 15-minute cadence, a
~2-3 minute ephemeral cluster startup is a real, material overhead
fraction of total run time. This job submits to a small, always-on
PERSISTENT cluster instead of creating/deleting a cluster every run —
the cluster itself is provisioned once via Terraform
(terraform/modules/dataproc-cluster with is_ha_cluster where warranted)
and referenced here by name, not created/destroyed per DAG run.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.google.cloud.operators.dataproc import DataprocSubmitJobOperator

PROJECT_ID = "{{ var.value.gcp_project_id }}"
REGION = "{{ var.value.gcp_region }}"
ARTIFACT_BUCKET = "{{ var.value.artifact_bucket }}"
JOB_VERSION = "{{ var.value.inventory_job_version }}"
COMMON_LIB_VERSION = "{{ var.value.common_lib_version }}"

# Persistent cluster, per the topology decision above — not created/
# deleted by this DAG.
PERSISTENT_CLUSTER_NAME = "{{ var.value.inventory_persistent_cluster_name }}"

default_args = {
    "owner": "data-engineering-inventory",
    "retries": 3,  # Tier 1
    "retry_delay": timedelta(minutes=2),  # short delay — next window is only 15 min away
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=10),
    "sla": timedelta(minutes=12),  # must finish well within the 15-min cadence
    "start_date": datetime(2026, 1, 1),
    "params": {"tier": 1},
}

with DAG(
    dag_id="inventory_inventory_sync_intraday",
    schedule_interval="*/15 * * * *",  # matches the on-prem cron cadence exactly
    default_args=default_args,
    catchup=False,
    max_active_runs=1,  # a run must finish before the next window's run starts
    tags=["inventory", "tier-1", "high-frequency", "wave-0-pilot"],
) as dag:

    submit_inventory_sync = DataprocSubmitJobOperator(
        task_id="submit_inventory_sync",
        project_id=PROJECT_ID,
        region=REGION,
        job={
            "reference": {"job_id": "inventory-sync-{{ ts_nodash }}"},
            "placement": {"cluster_name": PERSISTENT_CLUSTER_NAME},
            "pyspark_job": {
                "main_python_file_uri": (
                    f"gs://{ARTIFACT_BUCKET}/jobs/inventory-sync-intraday/"
                    f"{JOB_VERSION}/main.py"
                ),
                "python_file_uris": [
                    f"gs://{ARTIFACT_BUCKET}/libs/dp-spark-common-{COMMON_LIB_VERSION}.zip",
                    f"gs://{ARTIFACT_BUCKET}/jobs/inventory-sync-intraday/{JOB_VERSION}/inventory_sync_intraday.zip",
                ],
                "args": [
                    "--env", "{{ var.value.environment }}",
                    "--window-id", "{{ ts_nodash[:13] }}",  # YYYYMMDDTHHMM, minute precision
                ],
            },
        },
    )
    # No create/delete cluster tasks — see topology decision note above.
    # No sensor either — this job has no upstream data-availability
    # precondition (WMS deltas either exist for this window or the run
    # correctly processes zero deltas, per test_delta_application.py
    # "item with no delta this window is unchanged").
