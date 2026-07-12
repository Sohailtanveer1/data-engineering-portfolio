# Cron & Shell Script Conversion

**Purpose:** Convert every cron-triggered shell script identified in
[`02-dependency-analysis/methodology/04-shell-script-and-cron-dependencies.md`](../02-dependency-analysis/methodology/04-shell-script-and-cron-dependencies.md)
into a Composer DAG, deliberately eliminating the edge-node dependency and
undocumented-logic risks that category of finding surfaced.
**Owner:** Platform Engineering.

---

## Conversion principle: extract, don't wrap

The single most important decision in this conversion: **do not simply
wrap the existing shell script in a Composer `BashOperator` and call it
migrated.** Per
[`02-dependency-analysis/methodology/04-shell-script-and-cron-dependencies.md`](../02-dependency-analysis/methodology/04-shell-script-and-cron-dependencies.md),
these shell scripts often contain real business logic (retry handling,
marker file conventions, secondary cleanup steps, email notifications)
that should be extracted into tested Python/Spark code and explicit
Airflow task structure — not preserved as an opaque shell script now
running inside Composer.

## Conversion procedure

1. **Fully read and decompose the shell script** into its distinct logical
   steps (per the call-graph tracing already done in
   [`02-dependency-analysis/methodology/04-shell-script-and-cron-dependencies.md`](../02-dependency-analysis/methodology/04-shell-script-and-cron-dependencies.md)).
2. **Classify each step**:
   - Spark job invocation → `DataprocSubmitJobOperator`
   - File existence/marker check → Airflow Sensor
   - Cleanup/housekeeping → in most cases, replaced entirely by GCS
     lifecycle policies (per
     [`04-target-architecture/04-storage-architecture.md`](../04-target-architecture/04-storage-architecture.md))
     rather than reimplemented as a task
   - Notification (email, Slack) → Airflow's native `on_failure_callback`/
     `on_success_callback` or a dedicated notification operator, per
     [`05-monitoring-retries-and-alerts.md`](05-monitoring-retries-and-alerts.md)
   - Retry logic → Airflow task-level `retries`/`retry_delay`, combined
     with the operation-level retry pattern already built into shared
     Spark job code (per
     [`07-spark-migration/06-logging-and-error-handling.md`](../07-spark-migration/06-logging-and-error-handling.md))
   - Genuine remaining orchestration glue (rare, after the above) →
     `BashOperator` or, preferably, a small tested `PythonOperator`
     callable
3. **Remove any remaining hardcoded values** — paths, hostnames — through
   the same configuration pattern used everywhere else
   (Composer Variables, per
   [`06-variables-connections-and-secrets.md`](06-variables-connections-and-secrets.md)).
4. **Reconcile every discovered cron entry** against the resulting DAG
   set — every cron entry from
   [`01-discovery/inventories/10-scheduler-inventory.md`](../01-discovery/inventories/10-scheduler-inventory.md)
   must map to exactly one DAG, with no orphaned or duplicated coverage.

## Handling orphaned/unowned cron jobs

For any cron entry with no confirmed owner (e.g., the illustrative
`legacy_vendor_feed_2019` example from
[`01-discovery/inventories/06-job-inventory.md`](../01-discovery/inventories/06-job-inventory.md)):
resolve ownership and purpose *before* converting it to a DAG — do not
migrate an unexplained job by default just because it currently runs; this
is exactly the retirement-vs-migrate decision point flagged in Discovery.

## Common Mistakes

- Wrapping an entire multi-step shell script in a single `BashOperator`
  task — this produces a DAG with no visibility into which internal step
  failed, defeating one of Composer's main operational benefits over cron
  (per-task status, retry, and alerting granularity).
- Silently dropping a housekeeping/cleanup step during conversion without
  confirming a GCS lifecycle policy actually replaces its function — an
  unaddressed cleanup gap can cause unbounded storage growth on the new
  platform.

## Production Notes

For any cron job found running on a non-standard or undocumented edge
node during
[`02-dependency-analysis/methodology/04-shell-script-and-cron-dependencies.md`](../02-dependency-analysis/methodology/04-shell-script-and-cron-dependencies.md)
discovery, treat its conversion with extra scrutiny — jobs living outside
the "normal" scheduling infrastructure are statistically more likely to
carry undocumented, business-relevant behavior that a rushed conversion
could lose.
