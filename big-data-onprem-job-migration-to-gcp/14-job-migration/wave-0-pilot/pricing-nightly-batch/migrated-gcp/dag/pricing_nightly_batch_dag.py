"""
pricing_pricing_nightly_batch — Cloud Composer DAG for the migrated job.

Replaces pricing_nightly_coordinator.xml (see ../../on-prem-source/) —
same daily schedule, but the previously-undocumented "assume
inventory_sync_intraday finished by 01:00" assumption from the Oozie
version is now an explicit GCSObjectExistsSensor, per
09-composer-migration/01-oozie-to-composer-conversion.md.

No business logic here — orchestration only, per
09-composer-migration/04-dag-best-practices.md.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.google.cloud.operators.dataproc import (
    DataprocCreateClusterOperator,
    DataprocDeleteClusterOperator,
    DataprocSubmitJobOperator,
)
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistsSensor

PROJECT_ID = "{{ var.value.gcp_project_id }}"
REGION = "{{ var.value.gcp_region }}"
ARTIFACT_BUCKET = "{{ var.value.artifact_bucket }}"
JOB_VERSION = "{{ var.value.pricing_job_version }}"
COMMON_LIB_VERSION = "{{ var.value.common_lib_version }}"

CLUSTER_NAME = "pricing-nightly-{{ ds_nodash }}"

CLUSTER_CONFIG = {
    "master_config": {"num_instances": 1, "machine_type_uri": "n2-standard-4"},
    "worker_config": {"num_instances": 4, "machine_type_uri": "n2-standard-16"},
    "gce_cluster_config": {
        "subnetwork_uri": "{{ var.value.dataproc_subnet }}",
        "internal_ip_only": True,
        "service_account": "{{ var.value.pricing_etl_service_account }}",
    },
    "software_config": {
        "properties": {"spark:spark.sql.adaptive.enabled": "true"},
    },
}

default_args = {
    "owner": "data-engineering-pricing",
    "retries": 3,  # Tier 1 job
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=30),
    "sla": timedelta(hours=3),  # per 01-discovery/inventories/01-sla-inventory.md
    "start_date": datetime(2026, 1, 1),
    "params": {"tier": 1},
}

with DAG(
    dag_id="pricing_pricing_nightly_batch",
    schedule_interval="0 1 * * *",  # matches the on-prem Oozie coordinator frequency
    default_args=default_args,
    catchup=False,
    tags=["pricing", "tier-1", "batch", "wave-0-pilot"],
) as dag:

    wait_for_inventory_sync = GCSObjectExistsSensor(
        task_id="wait_for_inventory_sync_marker",
        bucket="{{ var.value.environment }}-inventory-curated",
        object="dt={{ ds }}/_SUCCESS",
        mode="reschedule",
        poke_interval=300,
        timeout=timedelta(hours=2).total_seconds(),
    )

    create_cluster = DataprocCreateClusterOperator(
        task_id="create_cluster",
        project_id=PROJECT_ID,
        region=REGION,
        cluster_name=CLUSTER_NAME,
        cluster_config=CLUSTER_CONFIG,
    )

    submit_pricing_job = DataprocSubmitJobOperator(
        task_id="submit_pricing_job",
        project_id=PROJECT_ID,
        region=REGION,
        job={
            "reference": {"job_id": "pricing-nightly-{{ ds_nodash }}"},
            "placement": {"cluster_name": CLUSTER_NAME},
            "pyspark_job": {
                "main_python_file_uri": (
                    f"gs://{ARTIFACT_BUCKET}/jobs/pricing-nightly-batch/"
                    f"{JOB_VERSION}/main.py"
                ),
                "python_file_uris": [
                    f"gs://{ARTIFACT_BUCKET}/libs/dp-spark-common-{COMMON_LIB_VERSION}.zip",
                    f"gs://{ARTIFACT_BUCKET}/jobs/pricing-nightly-batch/{JOB_VERSION}/pricing_nightly_batch.zip",
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
        trigger_rule="all_done",
    )

    wait_for_inventory_sync >> create_cluster >> submit_pricing_job >> delete_cluster
