# Dataproc Job Submission Patterns

**Purpose:** Define the standardized way every migrated Spark job is
submitted to Dataproc — replacing the inconsistent client/cluster mode
mix and manual `spark-submit` patterns found in
[`03-current-environment/03-spark-environment-assessment.md`](../03-current-environment/03-spark-environment-assessment.md).
**Owner:** Platform Engineering.

---

## Standard submission pattern

Every job is submitted via **Cloud Composer**, using the compute pattern
decided per job family in
[`04-target-architecture/03-compute-architecture.md`](../04-target-architecture/03-compute-architecture.md).
Manual, ad-hoc `spark-submit` from a human-operated edge node is not a
supported production pattern — this eliminates pain point #8 (client-mode
edge-node dependencies) from
[`03-current-environment/09-pain-points-and-bottlenecks.md`](../03-current-environment/09-pain-points-and-bottlenecks.md)
entirely, since there is no edge node in the target pattern.

### Ephemeral cluster pattern (default)

```python
# Composer DAG excerpt — see 09-composer-migration/ for full DAG patterns
create_cluster = DataprocCreateClusterOperator(
    task_id="create_cluster",
    project_id="{{ var.value.gcp_project_id }}",
    cluster_name="pricing-nightly-{{ ds_nodash }}",
    region="{{ var.value.gcp_region }}",
    cluster_config=CLUSTER_CONFIG,  # from 12-cluster-design/ per-job-family template
)

submit_job = DataprocSubmitJobOperator(
    task_id="submit_pricing_job",
    project_id="{{ var.value.gcp_project_id }}",
    region="{{ var.value.gcp_region }}",
    job={
        "reference": {"job_id": "pricing-nightly-{{ ds_nodash }}"},
        "placement": {"cluster_name": "pricing-nightly-{{ ds_nodash }}"},
        "pyspark_job": {
            "main_python_file_uri": "gs://{{ var.value.artifact_bucket }}/jobs/pricing-nightly-batch/{{ var.value.pricing_job_version }}/main.py",
            "python_file_uris": [
                "gs://{{ var.value.artifact_bucket }}/libs/dp-spark-common-{{ var.value.common_lib_version }}.zip"
            ],
            "args": ["--env", "{{ var.value.environment }}", "--run-date", "{{ ds }}"],
            "properties": {
                "spark.sql.adaptive.enabled": "true",
            },
        },
    },
)

delete_cluster = DataprocDeleteClusterOperator(
    task_id="delete_cluster",
    project_id="{{ var.value.gcp_project_id }}",
    cluster_name="pricing-nightly-{{ ds_nodash }}",
    region="{{ var.value.gcp_region }}",
    trigger_rule="all_done",  # delete even if the job failed — never leave a cluster running
)

create_cluster >> submit_job >> delete_cluster
```

`trigger_rule="all_done"` on the delete step is mandatory for every job —
a cluster left running after a job failure is a direct, avoidable cost
leak, addressed in
[`19-cost-optimization/`](../19-cost-optimization/README.md).

### Dataproc Serverless pattern (for irregular/backfill workloads)

```python
submit_batch = DataprocCreateBatchOperator(
    task_id="submit_batch",
    project_id="{{ var.value.gcp_project_id }}",
    region="{{ var.value.gcp_region }}",
    batch={
        "pyspark_batch": {
            "main_python_file_uri": "gs://{{ var.value.artifact_bucket }}/jobs/backfill-job/main.py",
            "python_file_uris": ["gs://{{ var.value.artifact_bucket }}/libs/dp-spark-common-{{ var.value.common_lib_version }}.zip"],
        },
        "runtime_config": {"version": "{{ var.value.dataproc_serverless_runtime_version }}"},
    },
    batch_id="backfill-job-{{ ds_nodash }}",
)
```

## Cluster configuration is per-job-family, not per-job

Cluster configuration (machine types, worker count, autoscaling policy,
initialization actions) is defined once per **job family** (a group of
jobs with similar resource profiles, per
[`01-discovery/inventories/08-spark-inventory.md`](../01-discovery/inventories/08-spark-inventory.md)),
not hand-tuned per individual job — see
[`12-cluster-design/`](../12-cluster-design/README.md) for the full
templating approach. This keeps the submission pattern consistent and
avoids per-job configuration drift.

## Initialization actions

Any cluster-level dependency that can't be handled via job-level
`python_file_uris`/`jar_file_uris` (e.g., an OS-level package, a custom
monitoring agent) is installed via a Dataproc initialization action script,
stored and versioned in [`scripts/`](../scripts/README.md) and referenced
from the Terraform cluster module in
[`13-infrastructure/`](../13-infrastructure/README.md) — never installed
manually/imperatively on a running cluster.

## Common Mistakes

- Submitting jobs via manual `gcloud dataproc jobs submit` from an
  engineer's workstation "just this once" — this reintroduces exactly the
  undocumented, person-dependent operational pattern flagged as pain point
  #7 in
  [`03-current-environment/09-pain-points-and-bottlenecks.md`](../03-current-environment/09-pain-points-and-bottlenecks.md).
- Forgetting `trigger_rule="all_done"` on cluster deletion, leaving failed
  job runs with orphaned, billing clusters.

## Production Notes

For Tier 1 jobs, verify cluster creation and deletion both succeed
reliably under failure injection testing (per
[`15-testing/`](../15-testing/README.md) chaos testing) before relying on
this pattern in production — an ephemeral cluster pattern that fails to
clean up properly under certain failure modes is both a cost and a
security exposure (an orphaned cluster is unpatched, unmonitored
infrastructure).
