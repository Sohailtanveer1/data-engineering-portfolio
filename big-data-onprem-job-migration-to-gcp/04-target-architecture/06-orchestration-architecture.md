# Orchestration Architecture

**Purpose:** Establish the high-level Cloud Composer deployment pattern —
environment placement, DAG organization strategy, and how orchestration
connects to the compute and storage layers — as the architectural
foundation [`09-composer-migration/`](../09-composer-migration/README.md)
builds detailed DAG patterns against.
**Owner:** Platform Engineering + Cloud/DevOps.

---

## Composer environment placement

| Environment | Composer Environment | Notes |
|---|---|---|
| `dev` | One Composer environment in `data-platform-dev` | Shared by all engineers for DAG development/testing |
| `qa` | One Composer environment in `data-platform-qa` | Automated integration test execution target |
| `stage` | One Composer environment in `data-platform-stage` | Cutover rehearsal target, production-equivalent configuration |
| `prod` | One Composer environment in `data-platform-prod` | Production orchestration only |

One Composer environment per GCP project/environment — not a single shared
Composer environment across environments — consistent with the full
environment isolation constraint (C4) in
[`00-project-overview/06-assumptions-and-constraints.md`](../00-project-overview/06-assumptions-and-constraints.md).

## DAG organization strategy

DAGs are organized **by business/data domain**, mirroring the team
ownership structure already established in
[`01-discovery/inventories/06-job-inventory.md`](../01-discovery/inventories/06-job-inventory.md),
not by technical job type:

```
dags/
├── pricing/
│   ├── pricing_nightly_batch_dag.py
├── fraud/
│   ├── fraud_score_hourly_dag.py
├── finance/
│   ├── finance_gl_reconciliation_dag.py
├── inventory/
│   ├── inventory_sync_intraday_dag.py
└── common/
    ├── operators/           Shared custom operators
    ├── sensors/             Shared custom sensors
    └── config/              Shared config-loading utilities
```

This mirrors the current per-team Oozie bundle / cron ownership pattern
documented in
[`01-discovery/inventories/10-scheduler-inventory.md`](../01-discovery/inventories/10-scheduler-inventory.md),
minimizing the mental-model shift for job owners while modernizing the
underlying orchestration technology. Full DAG authoring patterns
(dynamic DAG generation, retry/alerting conventions) are detailed in
[`09-composer-migration/`](../09-composer-migration/README.md).

## How orchestration connects to compute

Composer DAGs **do not run Spark code directly** — they orchestrate
Dataproc cluster lifecycle and job submission via GCP-native Airflow
operators (`DataprocCreateClusterOperator`,
`DataprocSubmitJobOperator`, `DataprocDeleteClusterOperator`, or
`DataprocCreateBatchOperator` for Dataproc Serverless), per the compute
patterns in
[`03-compute-architecture.md`](03-compute-architecture.md). This is a
deliberate separation of concerns: orchestration logic (scheduling,
dependencies, retries, alerting) lives in Composer; data processing logic
lives in versioned, independently-testable Spark job code (see
[`07-spark-migration/`](../07-spark-migration/README.md)).

## Variables, connections, and secrets

| Configuration Type | Storage Mechanism | Why |
|---|---|---|
| Environment-specific values (project ID, bucket names, cluster names) | Composer Variables, scoped per environment | Keeps DAG code identical across dev/qa/stage/prod — only Variables differ |
| Credentials (API keys, database passwords) | Secret Manager, referenced via Composer's Secret Manager backend integration | Never stored as plaintext Airflow Variables or Connections |
| External system connection details (non-secret) | Airflow Connections, or Composer Variables where simpler | |

This directly resolves the plaintext-credential findings flagged in
[`01-discovery/inventories/12-external-dependencies.md`](../01-discovery/inventories/12-external-dependencies.md).

## Data-availability-driven DAGs

Per the scheduler dependency analysis in
[`02-dependency-analysis/methodology/05-scheduler-workflow-dependencies.md`](../02-dependency-analysis/methodology/05-scheduler-workflow-dependencies.md),
jobs currently triggered by data-availability (not just time) use Airflow
sensors or deferrable operators (e.g., a GCS object sensor, or a
Dataproc/BigQuery job-completion sensor) rather than being force-fit into
pure time-based schedules — full patterns in
[`09-composer-migration/`](../09-composer-migration/README.md).

## Common Mistakes

- Organizing DAGs by technical layer (e.g., all "extract" DAGs together,
  all "transform" DAGs together) instead of by business domain — this
  makes ownership and on-call routing harder to reason about and diverges
  from how the current platform's teams already think about their jobs.
- Embedding actual Spark transformation logic directly inside DAG files —
  this couples orchestration and business logic, making both harder to
  test independently (see the OOP/testability principles in
  [`07-spark-migration/`](../07-spark-migration/README.md)).

## Production Notes

Composer environment sizing (worker count, node pool configuration) for
`prod` must account for the full DAG count and peak concurrent task
execution volume from
[`01-discovery/inventories/06-job-inventory.md`](../01-discovery/inventories/06-job-inventory.md)
and
[`01-discovery/inventories/10-scheduler-inventory.md`](../01-discovery/inventories/10-scheduler-inventory.md)
— undersizing Composer itself (as opposed to the Dataproc clusters it
orchestrates) is a common oversight that causes DAG scheduling delays
independent of any actual data processing bottleneck.
