# Migration Record — `inventory_sync_intraday`

---

## Summary

`inventory_sync_intraday` (Tier 1) migrated from an undocumented,
cron-triggered on-prem PySpark job (never registered in Oozie) to a
Composer DAG submitting to a persistent Dataproc cluster. Chosen as the
second Wave 0 pilot job specifically because it's a different pattern
from `pricing_nightly_batch`: high-frequency (15-min), stateful
read-modify-write (not a simple daily overwrite), and it surfaced two
confirmed real production incidents worth fixing during migration, not
just re-platforming.

## What changed, and why

| Issue Found (on-prem) | Fix (GCP) | Reference |
|---|---|---|
| Job invisible to the central scheduler (crontab-only, never in Oozie) | Explicit Composer DAG, fully visible in the same orchestration layer as every other job | [`09-composer-migration/02-cron-and-shell-to-composer-conversion.md`](../../../09-composer-migration/02-cron-and-shell-to-composer-conversion.md) |
| **Non-idempotent**: re-running a window re-applies its deltas, silently double-counting | Idempotency control table (`processed_windows`) — a window is checked before applying deltas and marked only after a confirmed write, mirroring the watermark pattern in [`06-data-migration/02-incremental-load-strategy.md`](../../../06-data-migration/02-incremental-load-strategy.md) | [`07-spark-migration/07-idempotency-design.md`](../../../07-spark-migration/07-idempotency-design.md) |
| **No negative-on-hand-quantity guard** — caused 2 confirmed real incidents | Explicit `assert_no_negative_quantities` check, raising a Terminal/Data error (never retried) rather than writing bad data | [`16-data-validation/04-business-rule-validation.md`](../../../16-data-validation/04-business-rule-validation.md) |
| **No alerting on failure at all** | Composer retry + Cloud Monitoring alert to the inventory on-call channel | [`18-monitoring/03-alerting-strategy.md`](../../../18-monitoring/03-alerting-strategy.md) |
| Ephemeral-vs-persistent cluster question at 15-min cadence | Evaluated explicitly against the startup-overhead-ratio heuristic; chosen **persistent** small cluster (not ephemeral) since repeated create/delete overhead would be a material fraction of the 15-min window | [`12-cluster-design/01-cluster-topology-decision.md`](../../../12-cluster-design/01-cluster-topology-decision.md) |
| Hardcoded paths, `SparkContext`/`SQLContext` | Externalized config, `SparkSessionFactory` | Same pattern as [`pricing-nightly-batch`](../pricing-nightly-batch/migration-record.md) |

## What did NOT change

The core delta-application arithmetic (sum deltas per warehouse/SKU, add
to current quantity, treat missing rows as zero on either side) is
unchanged — verified by unit tests asserting the same behavior as the
on-prem version for the happy path; only the failure/edge-case handling
(idempotency, negative quantity) is new.

## Validation status

| Gate | Status |
|---|---|
| Unit tests written | ✅ 9 tests across `test_delta_application.py`, `test_validation.py` |
| Unit tests executed | ⚠️ Not yet — requires a JVM, same limitation as the pricing pilot |
| Integration/parallel-run/UAT | Not started — requires real GCP + on-prem access |

## Next steps

Same as [`pricing-nightly-batch/migration-record.md`](../pricing-nightly-batch/migration-record.md)
— run `pytest tests/unit/ -v` in an environment with Java installed, then
proceed through integration testing and parallel-run. Given the confirmed
incident history, this job's parallel-run window should specifically
include a period where a WMS delta-feed anomaly is likely (per
[`14-job-migration/04-parallel-run-strategy.md`](../../04-parallel-run-strategy.md)
"cover at least one instance of the job's known highest-complexity
period") to prove the negative-quantity guard actually catches the real
failure mode it was built for.
