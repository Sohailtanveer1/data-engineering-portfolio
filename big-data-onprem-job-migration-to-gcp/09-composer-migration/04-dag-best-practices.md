# DAG Authoring Best Practices

**Purpose:** A concise, enforced standard for every DAG in this platform —
reviewed as part of [`ci-cd/`](../ci-cd/README.md) pull request checks, not
left to individual preference.
**Owner:** Platform Engineering.

---

## Standards

1. **No business logic in DAG files.** DAGs orchestrate; they never
   transform data or compute business values directly. All actual
   processing happens in the tested Spark job code from
   [`07-spark-migration/`](../07-spark-migration/README.md). A DAG file
   should be readable as a sequence of named steps, not a place to debug
   business logic.
2. **Idempotent task design.** Every task must be safely re-runnable —
   this follows directly from the idempotency requirement in
   [`07-spark-migration/07-idempotency-design.md`](../07-spark-migration/07-idempotency-design.md)
   and is what makes Airflow's native retry and backfill capabilities safe
   to use.
3. **Explicit, not implicit, task dependencies.** Use `>>`/`<<` or
   `set_upstream`/`set_downstream` clearly — avoid relying on task
   ordering within the file as an implicit dependency signal.
4. **No top-level code that performs I/O or heavy computation.** Code at
   DAG-file module level runs on every single DAG-parsing cycle (which
   happens frequently, independent of actual task execution) — any
   database call, API call, or expensive computation at this level
   creates real, avoidable load on the Composer environment and external
   systems. Configuration should be loaded from Composer Variables
   (cheap, cached) not fetched live from an external system at parse time.
5. **Consistent naming.** DAG IDs and task IDs follow the naming
   convention in
   [`04-target-architecture/02-landing-zone-and-project-structure.md`](../04-target-architecture/02-landing-zone-and-project-structure.md):
   `<data_domain>_<job_name>` for DAG IDs, descriptive snake_case for task
   IDs matching the pipeline step names used in the job's own code (per
   [`07-spark-migration/08-oop-design-patterns.md`](../07-spark-migration/08-oop-design-patterns.md)
   Builder pattern step names) for easy cross-referencing.
6. **Every DAG declares an owner and SLA.** Via the `default_args` `owner`
   field and task-level `sla` parameter, sourced from
   [`01-discovery/inventories/01-sla-inventory.md`](../01-discovery/inventories/01-sla-inventory.md)
   — not left as the Airflow default.
7. **Sensors use `mode="reschedule"`, not `mode="poke"`, for anything with
   a wait time over a few minutes.** `reschedule` mode releases the worker
   slot between checks, which matters materially at the scale of hundreds
   of DAGs sharing a Composer environment's worker capacity.
8. **Cluster teardown always runs, even on failure.** Per
   [`07-spark-migration/03-dataproc-submission-patterns.md`](../07-spark-migration/03-dataproc-submission-patterns.md),
   every ephemeral cluster's delete task uses `trigger_rule="all_done"`.

## Code review checklist (enforced in CI/CD)

- [ ] No business logic present in the DAG file
- [ ] No I/O or expensive computation at module top-level
- [ ] Every task is idempotent
- [ ] Owner and SLA declared
- [ ] Naming convention followed
- [ ] Cluster teardown (if applicable) uses `trigger_rule="all_done"`
- [ ] Retries and alerting configured per
      [`05-monitoring-retries-and-alerts.md`](05-monitoring-retries-and-alerts.md)
- [ ] No hardcoded secrets, project IDs, or bucket names — see
      [`06-variables-connections-and-secrets.md`](06-variables-connections-and-secrets.md)

## Common Mistakes

- Fetching configuration from an external API or database at DAG-file
  top-level "to keep it dynamic" — this is the single most common cause of
  Composer environment-wide slowdowns and external system load in
  production Airflow deployments.
- Copy-pasting a working DAG as the starting point for a new one and
  forgetting to update the owner/SLA/naming fields, leaving stale metadata
  that misleads on-call responders.

## Production Notes

Run a periodic audit (e.g., monthly, automated via
[`ci-cd/`](../ci-cd/README.md) or a scheduled check) of all `prod` DAGs
against this checklist — standards enforced only at initial PR review tend
to drift as DAGs are modified over time by different engineers.
