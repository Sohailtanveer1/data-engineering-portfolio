# Working DAG Examples

**Purpose:** Executable reference DAGs demonstrating the patterns
described in this folder's documentation.

## Files

| File | Demonstrates |
|---|---|
| [`pricing_nightly_batch_dag.py`](pricing_nightly_batch_dag.py) | A complete, production-shaped DAG: ephemeral Dataproc cluster lifecycle, standard retry/alerting config, SLA — see [`../04-dag-best-practices.md`](../04-dag-best-practices.md) and [`../05-monitoring-retries-and-alerts.md`](../05-monitoring-retries-and-alerts.md) |
| [`dynamic_dag_factory.py`](dynamic_dag_factory.py) | Dynamic DAG generation for a family of structurally similar jobs — see [`../03-dynamic-dag-generation.md`](../03-dynamic-dag-generation.md) |

## Running these examples

These files require `apache-airflow` and the Google provider package to
import/parse (they are not meant to be executed standalone outside a
Composer/Airflow environment):

```bash
pip install apache-airflow==2.7.3 apache-airflow-providers-google
python -c "import pricing_nightly_batch_dag"   # confirms the DAG parses without error
```

In an actual Composer environment, these files are placed directly in the
environment's `dags/` GCS folder (per the project layout in
[`../../04-target-architecture/06-orchestration-architecture.md`](../../04-target-architecture/06-orchestration-architecture.md))
and are picked up automatically by the Airflow scheduler.
