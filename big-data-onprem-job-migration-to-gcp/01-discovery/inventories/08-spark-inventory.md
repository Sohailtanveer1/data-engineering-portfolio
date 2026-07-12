# Spark Job Inventory

**Purpose:** Technical detail, per Spark job, required to scope
[`07-spark-migration/`](../../07-spark-migration/README.md) accurately —
version, language, resource footprint, and known technical debt. This is
more detailed than the master job inventory and applies only to jobs typed
"Spark" in [`06-job-inventory.md`](06-job-inventory.md).
**Owner:** Migration Program Lead, populated with Platform Engineering and
Developers.
**Inputs:** [`questions/06-developers.md`](../questions/06-developers.md),
YARN application history, Spark History Server (if retained), job
submission scripts.
**Outputs:** Directly scopes effort estimation and pattern design in
[`07-spark-migration/`](../../07-spark-migration/README.md).
**Validation method:** Cross-reference claimed Spark/Scala/Python version
against the actual JAR manifest or `spark-submit` invocation script, not
developer recollection alone.

---

## Spark inventory table

| Job ID | Language (Scala/PySpark/Java) | Spark Version | Submission Mode (client/cluster) | Avg. Executors | Executor Memory | Driver Memory | Uses RDD API? | Uses Deprecated APIs? | External JAR Dependencies | Idempotent? | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| EX-001 | Scala | 2.4.8 | cluster | 40 | 8g | 4g | Partial (legacy module) | Yes — `SQLContext`, old ML API | `internal-fraud-utils-1.3.jar` | No (overwrite semantics undocumented) | Flagged nervous by owner — see developer interview |
| EX-002 | PySpark | 2.4.8 | cluster (streaming) | 20 | 6g | 2g | No | Minor | `kafka-clients` connector | Yes (checkpointed) | Structured Streaming |
| EX-003 | Scala | 2.4.8 | cluster | 15 | 4g | 2g | No | No | none beyond core | Yes | |
| EX-008 | PySpark | 2.4.8 | client (manual trigger) | 30 | 8g | 4g | No | Minor | `internal-customer-utils-2.1.jar` | Unknown — needs verification | Manually triggered, ad-hoc |

_(Illustrative rows only — populate exhaustively for every Spark job
identified in [`06-job-inventory.md`](06-job-inventory.md).)_

## Aggregate findings to capture

Once the table above is complete, summarize:

- **Spark version distribution** — e.g., "94% of jobs on 2.4.8, 6% on
  1.6.x (legacy, needs major-version upgrade path)." This directly sizes
  the [`07-spark-migration/`](../../07-spark-migration/README.md) effort —
  a platform on a single consistent version is a much smaller lift than
  one with a long tail of legacy versions.
- **Language distribution** — Scala vs. PySpark vs. Java mix, since
  migration tooling/packaging patterns differ per language (see
  [`07-spark-migration/`](../../07-spark-migration/README.md)).
- **Deprecated API usage frequency** — which specific deprecated APIs
  appear most often, to prioritize the shared-library replacement pattern.
- **Non-idempotent job count** — every job flagged "No" or "Unknown" here
  needs explicit remediation before migration per the idempotency
  requirement in [`07-spark-migration/`](../../07-spark-migration/README.md).
- **Shared/external JAR dependency map** — which internal JARs are reused
  across many jobs (these become the first shared-library candidates
  rebuilt once in [`07-spark-migration/`](../../07-spark-migration/README.md)
  rather than migrated per-job).

## Common Mistakes

- Trusting a job's `pom.xml`/`build.sbt` declared Spark version over the
  actual cluster-installed version the job is really running against — the
  two can and do drift.
- Skipping resource footprint capture ("avg executors," "executor memory")
  — this data is required later for right-sizing Dataproc clusters in
  [`12-cluster-design/`](../../12-cluster-design/README.md); without it,
  cluster sizing starts from guesswork instead of evidence.

## Production Notes

For Tier 1 jobs specifically, capture resource footprint **during peak
trading load**, not steady state — under-provisioning a migrated
business-critical job's Dataproc cluster because sizing was based on an
average Tuesday is a direct path to a Black Friday incident.
