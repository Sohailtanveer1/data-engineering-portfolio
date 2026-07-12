# Identifying JAR, Library, and Shared Utility Dependencies

**Purpose:** Identify every external JAR, third-party library, and
internal shared utility a job depends on — the category of dependency most
likely to be reused across dozens of jobs simultaneously, which makes it
both high-leverage (fix once, benefit everywhere) and high-risk (break
once, break everywhere) for
[`07-spark-migration/`](../../07-spark-migration/README.md) packaging
design.
**Owner:** Platform Engineering.
**Inputs:** Build files (`pom.xml`, `build.sbt`, `requirements.txt`), JAR
manifests, `spark-submit --jars`/`--py-files` flags, internal artifact
repository (Nexus/Artifactory) metadata if present.

---

## What to look for

1. **Declared build dependencies** — every dependency listed in
   `pom.xml`/`build.sbt` (Scala/Java) or `requirements.txt`/`setup.py`
   (Python), including transitive dependencies, not just direct ones.
2. **Runtime-attached JARs** — anything passed via `--jars` or placed in a
   shared lib directory referenced by `spark.jars` / `spark.driver.extraClassPath`
   / `spark.executor.extraClassPath` that isn't captured in the build file
   (common for older Hadoop-era jobs that predate consistent build tooling).
3. **Internal shared libraries** — company-internal JARs/wheels (e.g.,
   `internal-fraud-utils`, `internal-customer-utils` as seen in the
   example Spark inventory) that wrap common logic (Spark session
   creation, GCS/HDFS I/O helpers, config loaders, logging setup). These
   are the highest-leverage migration targets — rebuilding one shared
   library correctly for GCP benefits every job that depends on it.
4. **Version pinning and conflicts** — cases where different jobs depend on
   different, possibly incompatible, versions of the same library. This
   must be resolved explicitly before consolidating onto a shared Dataproc
   image or shared library version in
   [`12-cluster-design/`](../../12-cluster-design/README.md).
5. **Native/non-JVM dependencies** — for PySpark jobs, any native binary or
   OS-level package dependency (e.g., a compiled C extension) that must be
   present on worker nodes — these need explicit handling via Dataproc
   custom images or initialization actions
   (see [`12-cluster-design/`](../../12-cluster-design/README.md)).

## Technique

1. **Build file dependency tree extraction.** Run `mvn dependency:tree` or
   `sbt dependencyTree` (Scala/Java) and `pip freeze` /
   `pipdeptree` (Python) per job repository to get the full, resolved
   dependency graph, not just the top-level declared list.
2. **JAR manifest inspection.** For any JAR present in a shared lib
   directory without a clear build-file origin, inspect its manifest
   (`unzip -p <jar> META-INF/MANIFEST.MF`) for versioning and origin clues.
3. **Cross-job reuse mapping.** Build a reverse index: for every internal
   shared library/JAR, list every job that depends on it (from the Spark
   inventory's "External JAR Dependencies" column). Libraries used by many
   Tier 1 jobs are the highest-priority candidates for careful, tested
   rebuilding in [`07-spark-migration/`](../../07-spark-migration/README.md)
   — they should not be migrated as an afterthought per-job.
4. **Version conflict detection.** Diff dependency versions across all
   jobs' resolved trees; flag any library with more than one version in
   active use across the estate.

## Output format

Produce a **shared-library reuse matrix**: rows are internal shared
libraries/JARs, columns are consuming Job IDs, cells indicate
version-in-use. This matrix directly determines the build order for
[`07-spark-migration/`](../../07-spark-migration/README.md) — shared
libraries with the widest reuse are migrated and validated first.

## Common Mistakes

- Only checking build files and missing JARs manually staged on edge nodes
  or shared HDFS lib directories — very common in older Hadoop estates that
  predate consistent CI/CD build practices.
- Assuming all jobs using "the same" internal shared library are actually
  on the same version of it — version drift across jobs is common and each
  version may need distinct compatibility validation.

## Production Notes

Any shared library touching Tier 1 job code (pricing, fraud, finance) needs
its own dedicated unit and integration test suite built as part of
[`07-spark-migration/`](../../07-spark-migration/README.md) — a bug
introduced while rebuilding a widely-shared utility has blast radius across
every job that depends on it, including jobs migrated in earlier, supposedly
"already done" waves.
