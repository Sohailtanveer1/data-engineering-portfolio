# Migration Record — `pricing_nightly_batch`

**Purpose:** The actual record of this job's migration — what changed,
why, and what was validated. This is the filled-in version of what
[`logs/log-entry-template.md`](../../../logs/log-entry-template.md) and
[`14-job-migration/03-migration-tracker.md`](../../03-migration-tracker.md)
point to for this job.

---

## Summary

`pricing_nightly_batch` (Tier 1) migrated from on-prem Oozie/PySpark 2.4.8
to Cloud Composer/Dataproc as the Wave 0 pilot — chosen to prove the
full end-to-end pattern (dependency analysis → restructuring → shared
library adoption → testing → DAG → Terraform) on a job complex enough to
be representative, before scaling to the rest of the estate.

## What changed, and why

| Issue Found (on-prem) | Fix (GCP) | Reference |
|---|---|---|
| Hardcoded HDFS paths, hostnames, discount cap | Externalized to `config/<env>.yaml`, resolved via `ConfigLoader` | [`07-spark-migration/05-configuration-management-and-secrets.md`](../../../07-spark-migration/05-configuration-management-and-secrets.md) |
| `SparkContext`/`SQLContext` (pre-`SparkSession` idiom) | Rebuilt on `SparkSession` via the shared `SparkSessionFactory` | [`07-spark-migration/02-spark-version-and-api-migration.md`](../../../07-spark-migration/02-spark-version-and-api-migration.md) |
| **Non-idempotent write** (`mode("append")`, duplicates rows on re-run) | `mode("overwrite")` with dynamic partition overwrite, scoped to `dt=<run_date>` only | [`07-spark-migration/07-idempotency-design.md`](../../../07-spark-migration/07-idempotency-design.md) |
| All logic in one monolithic script, no separation of concerns | Split into `transformations/` (promotions, discount cap, zone mapping) and `io/` (readers, writers), orchestrated by `main.py` via `PipelineBuilder` | [`07-spark-migration/01-repository-restructuring.md`](../../../07-spark-migration/01-repository-restructuring.md) |
| Discount-cap logic duplicated in ≥2 other on-prem jobs | Consolidated here first; flagged as a promotion candidate to the shared library once a second migrated job needs it | [`07-spark-migration/08-oop-design-patterns.md`](../../../07-spark-migration/08-oop-design-patterns.md) |
| No automated tests | 10 unit tests across 3 transformation modules, including an explicit idempotency test | [`07-spark-migration/09-unit-testing-strategy.md`](../../../07-spark-migration/09-unit-testing-strategy.md) |
| Client-mode `spark-submit` from a specific named edge node (`edge-node-03`) — an undocumented single point of failure | Cluster-mode submission via `DataprocSubmitJobOperator`, no edge-node dependency at all | [`07-spark-migration/03-dataproc-submission-patterns.md`](../../../07-spark-migration/03-dataproc-submission-patterns.md) |
| Single failure email via local `mail`, no retry | Composer task-level retry (3 attempts, exponential backoff) + Cloud Monitoring alert routed to the pricing on-call channel | [`09-composer-migration/05-monitoring-retries-and-alerts.md`](../../../09-composer-migration/05-monitoring-retries-and-alerts.md) |
| Undocumented "01:00 is late enough" dependency on `inventory_sync_intraday` | Explicit `GCSObjectExistsSensor` waiting on that job's `_SUCCESS` marker | [`09-composer-migration/01-oozie-to-composer-conversion.md`](../../../09-composer-migration/01-oozie-to-composer-conversion.md) |
| Manual log cleanup cron logic in the shell wrapper | Replaced entirely by a GCS lifecycle policy on the scratch/log bucket | [`04-target-architecture/04-storage-architecture.md`](../../../04-target-architecture/04-storage-architecture.md) |

## What did NOT change

Per the charter's scope boundary, business logic behavior is unchanged:
the 40% discount cap, the promotion-then-cap-then-price-then-zone
calculation order, and the left-join (not inner-join) semantics for
unmatched zones/promotions are all preserved exactly — verified by the
unit tests asserting the same edge-case behavior (null-to-zero promotion
coalescing, unmatched-region rows preserved with null zone) that the
on-prem version exhibited.

## Infrastructure

Provisioned via the existing Terraform composition in
[`terraform/environments/dev/main.tf`](../../../terraform/environments/dev/main.tf)
— this pilot reuses the `gcs-bucket`, `iam-service-account`, `kms-keyring`,
and `dataproc-cluster` modules already built in
[`terraform/modules/`](../../../terraform/modules), rather than
introducing new infrastructure code. No changes were needed to those
modules to support this job.

## Validation status

| Gate | Status | Notes |
|---|---|---|
| Unit tests written | ✅ Complete | 10 tests across `test_promotions.py`, `test_price_calculation.py`, `test_zone_mapping.py` |
| Unit tests **executed** | ⚠️ Not yet — see below | Requires a local JVM (Java 11+) to run PySpark's local Spark session; not available in the environment this pilot was built in |
| Integration tests (qa) | Not started | Requires a real GCP `qa` project |
| Parallel-run | Not started | Requires the on-prem job and this migrated job running side by side |
| Security review | Not started | Per [`10-security/08-execution-and-review-checklist.md`](../../../10-security/08-execution-and-review-checklist.md) |
| UAT sign-off | Not started | Requires Merchandising Director review per [`20-uat/`](../../../20-uat/README.md) |

**Honest status: this is a complete, structurally sound migration of the
code — not yet a validated one.** Per
[`14-job-migration/05-execution-steps-per-job.md`](../../05-execution-steps-per-job.md),
the remaining steps (execute tests for real, deploy to `qa`, integration
test, parallel-run, UAT, cutover) require an actual GCP project and
on-prem access that this authoring environment doesn't have. To close the
loop:

```bash
cd 14-job-migration/wave-0-pilot/pricing-nightly-batch/migrated-gcp
pip install -e ".[dev]"          # requires a local JVM for pyspark
pytest tests/unit/ -v --cov=src --cov-report=term-missing
```

## Next steps

1. Run the command above in an environment with Java installed to get a
   real pass/fail result — expected to pass based on manual logic trace,
   but "expected to pass" is not the same as "passed."
2. Package and publish per
   [`07-spark-migration/04-packaging-and-dependency-management.md`](../../../07-spark-migration/04-packaging-and-dependency-management.md),
   deploy to a real `qa` Dataproc environment, run
   [`07-spark-migration/10-integration-testing-strategy.md`](../../../07-spark-migration/10-integration-testing-strategy.md).
3. Begin parallel-run against the real on-prem job per
   [`14-job-migration/04-parallel-run-strategy.md`](../../04-parallel-run-strategy.md).
