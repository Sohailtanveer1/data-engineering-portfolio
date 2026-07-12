# Chaos Testing

**Purpose:** Deliberately inject failures into a non-production
environment to surface resilience gaps that no amount of happy-path or
even standard recovery testing reliably catches — the highest-rigor test
category, reserved for Tier 1 jobs and shared platform components.
**Owner:** Platform Engineering, run in `stage` only.

---

## Chaos experiments

| Experiment | What It Injects | What It Validates |
|---|---|---|
| Random worker termination during a running job | Simulates unexpected preemption/failure mid-task, beyond the planned preemptible-worker scenario in recovery testing | Task-level retry and idempotency robustness under unplanned, not just expected, interruption |
| Composer scheduler restart during active DAG runs | Simulates a Composer environment maintenance event or transient issue | DAG state recovery — do in-flight tasks resume correctly, not duplicate or hang |
| Secret Manager access temporarily denied | Simulates an IAM misconfiguration or transient Secret Manager outage | Job's error classification and alerting per [`07-spark-migration/06-logging-and-error-handling.md`](../07-spark-migration/06-logging-and-error-handling.md) — confirms this fails fast and clearly, not silently or with a confusing error |
| GCS API returning transient errors (429/503) during a job's read/write | Simulates GCS throttling under high concurrent load (a realistic peak-trading scenario) | The retry decorator pattern from [`07-spark-migration/examples/retry_decorator.py`](../07-spark-migration/examples/retry_decorator.py) actually recovers correctly |
| Simulated network partition between GCP and on-prem mid-sync | Simulates a VPN/Interconnect outage | Incremental sync resilience per [`05-storage-migration/04-incremental-sync-strategy.md`](../05-storage-migration/04-incremental-sync-strategy.md) |

## Chaos testing principles

1. **Never run in `prod`** during the migration program — reserved for
   `stage` exclusively, except for carefully pre-approved, narrowly-scoped
   "game days" after hypercare, with explicit sign-off.
2. **One variable at a time** — inject a single type of failure per
   experiment run, so results are attributable and interpretable, rather
   than combining multiple simultaneous failures (which is valuable for
   advanced resilience testing but should come after single-failure
   robustness is already confirmed).
3. **Automate where possible** — use a chaos engineering tool or scripted
   fault injection (e.g., a script that kills a specific worker VM, or a
   proxy that injects GCS API errors) rather than manual, one-off
   experimentation, so experiments are repeatable and can be re-run after
   a fix.

## What to do with findings

Every gap found via chaos testing is logged, root-caused, and fixed before
that job family proceeds to production — chaos testing findings are
treated with the same severity as a functional bug, not as "nice to know"
information.

## Common Mistakes

- Skipping chaos testing under schedule pressure, reasoning "recovery
  testing already covers failure scenarios" — recovery testing validates
  known, planned scenarios; chaos testing is specifically designed to
  surface unknown or combination failure modes recovery testing's
  scripted scenarios don't anticipate.
- Running chaos experiments without a clear rollback/stop mechanism for
  the experiment itself, risking an extended, unintended outage in the
  test environment.

## Production Notes

Prioritize chaos testing time for the shared Spark library and the
Composer DAG factory pattern (per
[`09-composer-migration/03-dynamic-dag-generation.md`](../09-composer-migration/03-dynamic-dag-generation.md))
specifically — given their wide blast radius across many jobs, a
resilience gap here has the highest aggregate impact if missed.
