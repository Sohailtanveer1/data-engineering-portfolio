# Oozie to Composer Conversion

**Purpose:** A systematic procedure for converting Oozie coordinators and
workflows to Composer DAGs, with explicit handling for the conditional/
branching logic and data-availability triggers identified as the
highest-risk translation category in
[`02-dependency-analysis/methodology/05-scheduler-workflow-dependencies.md`](../02-dependency-analysis/methodology/05-scheduler-workflow-dependencies.md).
**Owner:** Platform Engineering.

---

## Element-by-element conversion mapping

| Oozie Element | Composer/Airflow Equivalent |
|---|---|
| `<coordinator-app>` frequency | DAG `schedule_interval` (cron expression or preset) |
| `<workflow-app>` action sequence | Task dependencies (`task_a >> task_b`) |
| `<action><spark>` | `DataprocSubmitJobOperator` (per [`07-spark-migration/03-dataproc-submission-patterns.md`](../07-spark-migration/03-dataproc-submission-patterns.md)) |
| `<action><shell>` | `BashOperator` (only for genuinely lightweight orchestration glue — business logic should already have been moved into tested Python/Spark code, not left as shell) |
| `<action><hive>` | `BigQueryInsertJobOperator` / `DataprocSubmitJobOperator` (Hive action) depending on the table's target platform |
| `<decision>` node | Airflow `BranchPythonOperator`, or redesigned as explicit conditional logic in a Python callable |
| `<fork>`/`<join>` | Parallel task branches converging via Airflow's native dependency graph (`[task_a, task_b] >> task_c`) |
| Data-availability wait (via a preceding shell check or Oozie's dataset-driven coordinator input events) | Airflow Sensor (e.g., `GCSObjectExistsSensor`) or a deferrable operator |
| `<sla>` tag | Airflow `sla` parameter on the task/DAG, feeding [`05-monitoring-retries-and-alerts.md`](05-monitoring-retries-and-alerts.md) |

## Step-by-step conversion procedure

1. **Start from the extracted action graph**, not the raw XML — use the
   structured graph already built in
   [`02-dependency-analysis/methodology/05-scheduler-workflow-dependencies.md`](../02-dependency-analysis/methodology/05-scheduler-workflow-dependencies.md),
   including every decision-node branch.
2. **Convert each action** per the mapping table above.
3. **For every decision node**, confirm with the original developer (per
   [`01-discovery/questions/06-developers.md`](../01-discovery/questions/06-developers.md))
   the actual business condition being evaluated, and implement it as
   explicit, readable, tested Python logic in a `BranchPythonOperator`
   callable — not a black-box translation of the Oozie EL (Expression
   Language) condition.
4. **For every data-availability trigger**, replace the informal
   file/marker-check pattern with an explicit Airflow Sensor, configured
   with an appropriate timeout and poke interval (per
   [`04-dag-best-practices.md`](04-dag-best-practices.md)).
5. **Validate the converted DAG** against the original action graph — walk
   both side by side and confirm every action, dependency, and branch
   condition has a corresponding, behaviorally-equivalent element in the
   new DAG.

## Example: converting a decision node

**Original Oozie logic (paraphrased):** "If the fraud score exceeds the
configured threshold, run an additional manual-review-queue action;
otherwise proceed directly to output."

```python
def decide_review_path(**context):
    """
    Mirrors the original Oozie decision node condition, confirmed with
    the Fraud Engineering team during migration (see 01-discovery/questions/06-developers.md).
    Business rule: scores >= review_threshold require manual review queueing.
    """
    max_score = context["ti"].xcom_pull(task_ids="score_transactions", key="max_score")
    review_threshold = context["params"]["review_threshold"]
    return "queue_for_manual_review" if max_score >= review_threshold else "publish_scores"

decide_branch = BranchPythonOperator(
    task_id="decide_review_path",
    python_callable=decide_review_path,
)
```

This is deliberately more explicit and readable than the original Oozie EL
condition — a direct benefit of treating this as a redesign, not a
mechanical translation.

## Common Mistakes

- Translating a decision node's XML condition syntax literally without
  confirming its actual business intent — a syntactically correct
  translation of a poorly-understood condition can preserve a bug rather
  than fix or even notice it.
- Converting a data-availability check implemented as a Oozie shell action
  polling loop into a fixed Composer schedule delay ("just run 2 hours
  later, that's usually enough") instead of a proper Sensor — this
  reintroduces exactly the kind of fragile, timing-assumption-based logic
  the migration should be improving on.

## Production Notes

For any Tier 1 workflow with a decision node, require the decision logic's
Python implementation to be reviewed and explicitly signed off by both
Platform Engineering and the Business Owner's technical contact — not just
unit-tested — given how easy it is for a subtly wrong condition to pass a
narrow test suite while still being wrong for the real business case.
