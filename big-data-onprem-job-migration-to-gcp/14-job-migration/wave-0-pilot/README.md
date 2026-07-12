# Wave 0 Pilot

Real, complete job migrations executed as the pilot wave per
[`14-job-migration/02-wave-planning.md`](../02-wave-planning.md) — each
subfolder is one job, taken all the way from its actual on-prem source
through to a fully migrated, tested GCP implementation. Chosen
deliberately to cover three genuinely different migration patterns, not
three variations of the same thing.

## Jobs in this wave

| Job | Tier | Pattern | Tests | Status |
|---|---|---|---|---|
| [`pricing-nightly-batch/`](pricing-nightly-batch/) | 1 | Ephemeral Dataproc cluster, daily Oozie → Composer DAG | Written (10), not executable here — needs a JVM | Code complete — see [migration-record.md](pricing-nightly-batch/migration-record.md) |
| [`inventory-sync-intraday/`](inventory-sync-intraday/) | 1 | Persistent Dataproc cluster, high-frequency cron → Composer, stateful idempotency control table | Written (9), not executable here — needs a JVM | Code complete — see [migration-record.md](inventory-sync-intraday/migration-record.md) |
| [`finance-gl-reconciliation/`](finance-gl-reconciliation/) | 1 | No Dataproc — Hive → BigQuery `MERGE` directly, orchestrated via `BigQueryInsertJobOperator` | **16/16 actually passing** — pure Python, no JVM needed | Code complete, tests verified — see [migration-record.md](finance-gl-reconciliation/migration-record.md) |

## What each job demonstrates that the others don't

- **`pricing-nightly-batch`** — the baseline pattern: ephemeral cluster,
  shared library adoption, config externalization, idempotent
  partition-overwrite writes.
- **`inventory-sync-intraday`** — the ephemeral-vs-persistent cluster
  decision at high frequency, and idempotency for a *stateful*
  read-modify-write job (harder than a simple overwrite) via an explicit
  processed-windows control table.
- **`finance-gl-reconciliation`** — a job that doesn't need Spark/Dataproc
  at all; a real regulatory (SOX) business-rule gate that didn't exist
  on-prem; and the only pilot job whose tests could actually be executed
  and verified passing in this authoring environment.

## Adding another job to this wave

Follow the same structure: `on-prem-source/` (the real original),
`dependency-analysis.md`, `migrated-gcp/` (the full migration), and
`migration-record.md` (what changed and why, with an honest validation
status) — see any of the three jobs above as reference patterns.
