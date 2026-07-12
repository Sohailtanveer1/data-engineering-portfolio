"""
pricing_nightly_batch_dag — Production DAG reference example.

See: 09-composer-migration/04-dag-best-practices.md
     09-composer-migration/05-monitoring-retries-and-alerts.md

Orchestrates the illustrative EX-001 pricing_nightly_batch job (see
01-discovery/inventories/06-job-inventory.md) using the ephemeral
Dataproc cluster pattern from 07-spark-migration/03-dataproc-submission-patterns.md.

No business logic lives in this file — it orchestrates the already-tested
job package built in 07-spark-migration/.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.google.cloud.operators.dataproc import (
    DataprocCreateClusterOperator,
    DataprocDeleteClusterOperator,
    DataprocSubmitJobOperator,
)
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistsSensor

from dags.common.alerting import alert_on_task_failure, alert_on_sla_miss  # shared module, see 06-variables-connections-and-secrets.md
from dags.common.cluster_configs import PRICING_CLUSTER_CONFIG  # per-job-family config, see 12-cluster-design/

PROJECT_ID = "{{ var.value.gcp_project_id }}"
REGION = "{{ var.value.gcp_region }}"
ARTIFACT_BUCKET = "{{ var.value.artifact_bucket }}"
JOB_VERSION = "{{ var.value.pricing_job_version }}"
COMMON_LIB_VERSION = "{{ var.value.common_lib_version }}"

CLUSTER_NAME = "pricing-nightly-{{ ds_nodash }}"

default_args = {
    "owner": "data-engineering-pricing",
    "retries": 3,                                   # Tier 1 job — see 05-monitoring-retries-and-alerts.md
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=30),
    "on_failure_callback": alert_on_task_failure,
    "sla": timedelta(hours=3),                        # from 01-discovery/inventories/01-sla-inventory.md
    "start_date": datetime(2026, 1, 1),
    "params": {"tier": 1},
}

with DAG(
    dag_id="pricing_pricing_nightly_batch",           # <data_domain>_<job_name>
    schedule_interval="0 1 * * *",                     # matches on-prem Oozie coordinator frequency
    default_args=default_args,
    catchup=False,
    sla_miss_callback=alert_on_sla_miss,
    tags=["pricing", "tier-1", "batch"],
) as dag:

    # Data-availability precondition: upstream inventory sync must have
    # completed its final run of the prior day before pricing runs.
    # Replaces the informal marker-file check from the original Oozie
    # workflow — see 09-composer-migration/01-oozie-to-composer-conversion.md.
    wait_for_inventory_sync = GCSObjectExistsSensor(
        task_id="wait_for_inventory_sync_marker",
        bucket="{{ var.value.env }}-inventory-curated",
        object="dt={{ ds }}/_SUCCESS",
        mode="reschedule",                             # releases worker slot between checks
        poke_interval=300,
        timeout=timedelta(hours=2).total_seconds(),
    )

    create_cluster = DataprocCreateClusterOperator(
        task_id="create_cluster",
        project_id=PROJECT_ID,
        region=REGION,
        cluster_name=CLUSTER_NAME,
        cluster_config=PRICING_CLUSTER_CONFIG,
    )

    submit_pricing_job = DataprocSubmitJobOperator(
        task_id="submit_pricing_job",
        project_id=PROJECT_ID,
        region=REGION,
        job={
            "reference": {"job_id": f"pricing-nightly-{{{{ ds_nodash }}}}"},
            "placement": {"cluster_name": CLUSTER_NAME},
            "pyspark_job": {
                "main_python_file_uri": (
                    f"gs://{ARTIFACT_BUCKET}/jobs/pricing-nightly-batch/"
                    f"{JOB_VERSION}/main.py"
                ),
                "python_file_uris": [
                    f"gs://{ARTIFACT_BUCKET}/libs/dp-spark-common-{COMMON_LIB_VERSION}.zip"
                ],
                "args": ["--env", "{{ var.value.environment }}", "--run-date", "{{ ds }}"],
                "properties": {"spark.sql.adaptive.enabled": "true"},
            },
        },
    )

    delete_cluster = DataprocDeleteClusterOperator(
        task_id="delete_cluster",
        project_id=PROJECT_ID,
        region=REGION,
        cluster_name=CLUSTER_NAME,
        trigger_rule="all_done",                        # always clean up, even on failure
    )

    wait_for_inventory_sync >> create_cluster >> submit_pricing_job >> delete_cluster
