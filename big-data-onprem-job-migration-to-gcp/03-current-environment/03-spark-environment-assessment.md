# Spark Environment Assessment

**Purpose:** Document the current Spark runtime environment holistically —
cluster-wide defaults, installed version(s), and deployment mode — as
distinct from the per-job detail already captured in
[`01-discovery/inventories/08-spark-inventory.md`](../01-discovery/inventories/08-spark-inventory.md).
This document answers "what does Spark look like as a piece of platform
infrastructure," feeding directly into
[`07-spark-migration/`](../07-spark-migration/README.md) compatibility
planning.
**Owner:** Platform Engineering.
**Inputs:** `spark-defaults.conf`, `spark-env.sh`, installed Spark
distribution package/version, Spark History Server configuration.

---

## Installed Spark version(s)

| Spark Version | Scala Version | Deployment Location | Jobs Using It (approx. count) | End-of-support Status |
|---|---|---|---|---|
| _(e.g., 2.4.8)_ | _(e.g., 2.11)_ | Cluster-wide default | _(count)_ | _(check against Apache Spark / distro EOL)_ |
| _(e.g., 1.6.x, if any legacy remains)_ | _(e.g., 2.10)_ | _(specific nodes/jobs)_ | _(count)_ | Past EOL — legacy risk |

If more than one Spark version is installed side-by-side (common in
long-lived Hadoop estates), document how job submission selects which
version runs — this pattern must be explicitly replaced in
[`07-spark-migration/`](../07-spark-migration/README.md), since Dataproc
image-based version selection works differently.

## Cluster-wide Spark defaults

| Setting | Current Value | Migration Relevance |
|---|---|---|
| `spark.master` | _(yarn)_ | Confirms YARN-mode deployment, not standalone/Mesos |
| `spark.submit.deployMode` | _(client/cluster)_ | Client mode has edge-node dependencies that don't map cleanly to ephemeral Dataproc — flag for redesign |
| `spark.dynamicAllocation.enabled` | | Directly informs autoscaling design in [`12-cluster-design/`](../12-cluster-design/README.md) |
| `spark.sql.adaptive.enabled` (AQE) | | If disabled, this is a quick-win performance opportunity to enable during migration — see [`17-performance/`](../17-performance/README.md) |
| `spark.serializer` | | Confirm Kryo vs. Java default |
| `spark.eventLog.enabled` / `spark.eventLog.dir` | | Confirms whether Spark History Server data exists to mine for job-level detail |
| `spark.yarn.queue` default | | |

## Spark deployment pattern

| Question | Finding |
|---|---|
| Is Spark submitted via `spark-submit` CLI directly, via a wrapper script, or via a workflow engine action (Oozie Spark action)? | |
| Are there multiple, inconsistent submission patterns across teams? | |
| Is there a shared "gateway"/edge node configuration all jobs submit through? | |
| Are Python/PySpark environments managed via a shared virtualenv/conda environment, or per-job? | |

Inconsistent submission patterns across teams are common in older estates
and directly increase the effort estimate for
[`07-spark-migration/`](../07-spark-migration/README.md), since each
distinct pattern needs its own migration path to a standardized Dataproc
submission approach.

## Client-mode dependency audit

Any job running in `client` deploy mode has its Spark driver running on the
submitting edge node, which means it can carry **edge-node-local
dependencies** (local file paths, local Python packages, local environment
variables) invisible to a `cluster`-mode job. Every client-mode job
identified here should be flagged for extra scrutiny in
[`02-dependency-analysis/methodology/01-spark-job-dependencies.md`](../02-dependency-analysis/methodology/01-spark-job-dependencies.md),
since these dependencies are the ones most likely to be lost when the job
moves to a stateless Dataproc submission pattern.

## Common Mistakes

- Documenting the "official" supported Spark version without checking
  whether teams have unofficially installed or vendored a different
  version for their own jobs.
- Treating `spark-defaults.conf` values as universally applied — many jobs
  override cluster defaults via `--conf` flags in their submission
  scripts; the true effective configuration is per-job, not just the
  cluster default (cross-reference with
  [`01-discovery/inventories/08-spark-inventory.md`](../01-discovery/inventories/08-spark-inventory.md)).

## Production Notes

Confirm explicitly whether AQE, dynamic allocation, and other
performance-relevant Spark 3.x features are available given the current
version — if the estate is still on Spark 2.x, this is a strong argument
for treating the Spark version upgrade as a first-class, explicitly scoped
part of [`07-spark-migration/`](../07-spark-migration/README.md) rather
than an incidental side effect of re-platforming.
