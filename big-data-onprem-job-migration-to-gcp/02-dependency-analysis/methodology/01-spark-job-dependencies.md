# Identifying Spark Job Dependencies

**Purpose:** Establish a repeatable method for discovering everything a
given Spark job reads, writes, and requires to run — beyond what the
developer remembers.
**Owner:** Platform Engineering, with Data Engineering support.
**Inputs:** Spark job source code (Scala/PySpark), `spark-submit` launch
scripts, Spark History Server event logs (if retained).
**Outputs:** A per-job dependency card (see
[`templates/02-job-dependency-card-template.md`](../templates/02-job-dependency-card-template.md))
covering inputs, outputs, and runtime requirements.

---

## What to look for

1. **Read paths** — every `spark.read`, `sqlContext.read`, `hiveContext.table`,
   or raw `sc.textFile`/`sc.sequenceFile` call. Extract the literal path or
   table name; flag any path/table name built dynamically (via string
   concatenation or a config value) for manual review, since these can't be
   found by simple text search.
2. **Write paths** — every `.write`, `.saveAsTable`, `.insertInto` call.
   These define what other jobs might depend on downstream — cross-reference
   against [`09-downstream-consumer-analysis.md`](09-downstream-consumer-analysis.md).
3. **Broadcast variables / driver-side lookups** — small reference datasets
   loaded into the driver (e.g., a CSV lookup file, a small Hive table
   collected to the driver). These are easy to miss because they don't look
   like "the job's data," but they're a hard dependency.
4. **Configuration sources** — `SparkConf` values, `--conf` flags in the
   submit script, and any external config file (properties, YAML, JSON)
   the job loads at startup. Every hardcoded value found here is also a
   direct input to [`07-spark-migration/`](../../07-spark-migration/README.md)
   configuration externalization work.
5. **Runtime environment dependencies** — environment variables the job
   reads (`System.getenv` / `os.environ`), and any assumption about the
   node it runs on (local file paths, specific host resolution).

## Technique

1. **Static code search.** Grep the job's source for the read/write API
   calls listed above. For Scala/Java, also inspect compiled JAR contents
   (`javap`/decompilation) if source is unavailable for an older job.
2. **Submit script inspection.** Read the actual `spark-submit` command
   (not just the job code) — resource settings, `--files`, `--jars`,
   `--py-files`, and any `--conf` overrides often carry dependencies
   invisible in the job code itself.
3. **Spark History Server cross-check (if retained).** For jobs with
   retained history, pull the actual event log and inspect the
   `SparkListenerEnvironmentUpdate` event for the real runtime
   classpath and config — this is ground truth for what actually ran,
   independent of what the current source code claims.
4. **Dynamic path resolution — manual review required.** Any job building
   a path/table name from a variable (`s"/data/pricing/dt=$date"`) cannot
   be fully resolved by static analysis alone. Flag these explicitly and
   resolve by developer interview or by sampling actual HDFS access logs
   for the job's service account over a representative time window.

## Output format

Record findings in a
[per-job dependency card](../templates/02-job-dependency-card-template.md)
— one card per Job ID from
[`01-discovery/inventories/06-job-inventory.md`](../../01-discovery/inventories/06-job-inventory.md).

## Common Mistakes

- Trusting only the "happy path" code and missing dependencies in
  exception-handling or fallback branches (e.g., a job that reads a backup
  location only when the primary read fails — easy to miss, and it will
  eventually be exercised).
- Ignoring test/dev code paths still present in production job code
  (commented-out or feature-flagged blocks referencing paths that may
  still be live).

## Production Notes

For Tier 1 jobs, supplement static analysis with a short **live shadow
period**: temporarily instrument the job (or use existing audit logging on
HDFS/Hive access) to record every path actually touched during 2–4 real
production runs. This catches dynamic dependencies static analysis cannot
reliably resolve.
