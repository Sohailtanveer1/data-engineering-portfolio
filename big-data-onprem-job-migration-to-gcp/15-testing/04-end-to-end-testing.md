# End-to-End Testing

**Purpose:** Validate the full path from Composer DAG trigger through
Dataproc cluster lifecycle, job execution, and final output — the
integration point between orchestration (
[`09-composer-migration/`](../09-composer-migration/README.md)) and job
execution ([`07-spark-migration/`](../07-spark-migration/README.md)) that
neither layer's own tests fully cover in isolation.
**Owner:** QA.

---

## What end-to-end testing covers beyond integration testing

[`07-spark-migration/10-integration-testing-strategy.md`](../07-spark-migration/10-integration-testing-strategy.md)
tests a job's pipeline logic against real GCS/BigQuery. End-to-end testing
additionally validates:

- The actual Composer DAG triggers correctly on schedule (or via a
  manually-triggered test run).
- Cluster creation, job submission, and cluster deletion via the real
  Dataproc operators succeed, including under the `trigger_rule="all_done"`
  cleanup path when a deliberately-injected failure occurs.
- Sensors (data-availability waits, per
  [`09-composer-migration/01-oozie-to-composer-conversion.md`](../09-composer-migration/01-oozie-to-composer-conversion.md))
  correctly wait for and detect their trigger condition.
- Alerting fires correctly on a deliberately-injected task failure (per
  [`09-composer-migration/05-monitoring-retries-and-alerts.md`](../09-composer-migration/05-monitoring-retries-and-alerts.md)).
- Downstream consumers (a dependent DAG, a BI tool connection) receive
  correctly-formed, queryable output.

## End-to-end test scenarios (required per job)

1. **Full happy path** — DAG triggers, cluster lifecycle completes,
   correct output produced, no alerts fired.
2. **Sensor timeout** — the data-availability precondition is deliberately
   not met; confirm the sensor times out per its configured behavior and
   alerts correctly rather than hanging indefinitely or silently failing.
3. **Task failure and retry** — deliberately inject a failure in the
   submitted Spark job; confirm Composer's retry logic engages per
   [`09-composer-migration/05-monitoring-retries-and-alerts.md`](../09-composer-migration/05-monitoring-retries-and-alerts.md)
   and cluster teardown still executes via `trigger_rule="all_done"`.
4. **Downstream consumption** — for a job feeding another DAG or a BI
   tool, confirm the full chain works, not just the producing job in
   isolation.

## Automation

End-to-end tests run in `qa`/`stage` as part of
[`ci-cd/`](../ci-cd/README.md) pipeline gates before a job/DAG combination
is approved for production deployment — using real (small-scale) Dataproc
cluster creation, not a mock, since the goal is validating the actual
GCP-native operator behavior.

## Common Mistakes

- Testing only the happy path end-to-end and relying on unit tests alone
  for failure scenarios — failure-path behavior (retry, alerting, cleanup)
  is specifically an orchestration-layer concern that unit tests, scoped
  to job code alone, cannot validate.
- Running end-to-end tests against a shared, mutable `qa` DAG folder where
  concurrent test runs interfere with each other — use isolated,
  uniquely-named test DAG instances per test run.

## Production Notes

For Tier 1 jobs, the sensor-timeout and task-failure-and-retry scenarios
are mandatory, not optional — these are exactly the failure modes most
likely to occur in production and least likely to be caught by a
happy-path-only test suite.
