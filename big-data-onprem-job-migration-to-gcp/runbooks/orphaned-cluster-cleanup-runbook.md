# Runbook: Orphaned Cluster Cleanup

## Trigger

The "orphaned Dataproc cluster" alert fires per
[`12-cluster-design/06-cluster-policies-and-governance.md`](../12-cluster-design/06-cluster-policies-and-governance.md)
— a cluster has been running longer than its job family's expected
maximum duration.

## Diagnosis

1. Identify the cluster and its associated job/DAG run via its labels
   (`job_family`, `data_domain`).
2. Check whether the job is still genuinely running (a legitimately
   long-running run, e.g., an unusually large backfill) or has already
   finished/failed while the cluster failed to tear down.
3. Check the Composer DAG run's task status for the
   `DataprocDeleteClusterOperator` task — did it run and fail, or never
   trigger?

## Resolution

| Scenario | Action |
|---|---|
| Job legitimately still running | No action — false positive; consider adjusting the alert threshold per [`12-cluster-design/06-cluster-policies-and-governance.md`](../12-cluster-design/06-cluster-policies-and-governance.md) if this job family's expected duration was mis-calibrated |
| Job finished/failed, teardown task failed | Investigate why (check the teardown task's logs — a permissions issue, an API error); manually delete the cluster once confirmed safe; fix the underlying teardown failure cause |
| Job finished/failed, teardown task never triggered | This indicates a DAG bug (missing `trigger_rule="all_done"`, per [`07-spark-migration/03-dataproc-submission-patterns.md`](../07-spark-migration/03-dataproc-submission-patterns.md)) — manually delete the cluster, then fix the DAG and redeploy |

## Manual cluster deletion

```bash
gcloud dataproc clusters delete <cluster-name> \
  --project=<project-id> \
  --region=<region>
```

Confirm no job is actively using the cluster before deleting — check the
Dataproc jobs list for the cluster first.

## After resolution

Log per
[`documentation/issue-tracker.md`](../documentation/issue-tracker.md),
noting cost impact (per
[`19-cost-optimization/02-compute-cost-optimization.md`](../19-cost-optimization/02-compute-cost-optimization.md))
if the cluster ran orphaned for a significant duration. If root cause is
a DAG bug, treat as a code fix requiring the standard PR/review/deploy
process, not a manual production DAG edit.
