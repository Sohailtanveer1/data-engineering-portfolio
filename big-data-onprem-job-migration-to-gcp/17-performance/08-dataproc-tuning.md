# Dataproc-Specific Tuning

**Purpose:** Tuning considerations specific to running Spark on Dataproc
(as opposed to generic Spark tuning, or on-prem YARN tuning) — GCS I/O
characteristics, Dataproc image selection, and cluster-level settings
unique to this platform.
**Owner:** Platform Engineering.

---

## GCS connector tuning

| Setting | Guidance |
|---|---|
| `fs.gs.inputstream.fadvise` | Set to `RANDOM` for workloads with random access patterns (e.g., interactive queries), `SEQUENTIAL` for full-table scans typical of most batch jobs — mismatched fadvise mode is a common, easy-to-miss GCS read performance issue |
| `fs.gs.outputstream.upload.chunk.size` | Tune upward from default for jobs writing very large files, reducing per-chunk overhead |
| GCS request parallelism | Ensure sufficient executor count/cores to parallelize GCS reads adequately — GCS throughput scales with request parallelism more than with any single-connection tuning |

## Dataproc image and component selection

- Use the **latest stable Dataproc image** compatible with the target
  Spark version (per
  [`07-spark-migration/02-spark-version-and-api-migration.md`](../07-spark-migration/02-spark-version-and-api-migration.md))
  — newer images frequently include GCS connector and JVM performance
  improvements.
- Disable optional Dataproc components not needed by a given job family
  (e.g., Jupyter, Zeppelin on ephemeral batch-job clusters) to reduce
  cluster startup time and resource overhead.

## Network topology considerations

Ensure Dataproc clusters run in the **same region** as their primary GCS
buckets and BigQuery datasets (per
[`04-target-architecture/04-storage-architecture.md`](../04-target-architecture/04-storage-architecture.md)
regional strategy) — cross-region access adds latency and egress cost with
no corresponding benefit for the primary processing path.

## Cluster startup time optimization

For ephemeral clusters (the default pattern per
[`04-target-architecture/03-compute-architecture.md`](../04-target-architecture/03-compute-architecture.md)),
startup time directly affects every job's effective runtime:

| Technique | Impact |
|---|---|
| Custom images (per [`12-cluster-design/07-initialization-actions-and-custom-images.md`](../12-cluster-design/07-initialization-actions-and-custom-images.md)) instead of heavy init actions | Reduces startup time for jobs with non-trivial dependencies |
| Minimal initial worker count with fast autoscale-up | Reduces time-to-first-availability vs. provisioning full peak capacity at startup |
| Avoiding unnecessary optional components | Reduces cluster initialization overhead |

## Common Mistakes

- Using default GCS connector `fadvise` settings without matching them to
  the job's actual read pattern.
- Running Dataproc clusters and their primary GCS buckets in different
  regions "because that's where the project happened to be created,"
  incurring unnecessary latency and egress cost on every single job run.

## Production Notes

For every job family, measure actual cluster startup-to-job-start latency
during
[`15-testing/08-performance-testing-overview.md`](../15-testing/08-performance-testing-overview.md)
and factor it explicitly into the job's overall SLA budget — a job that
processes data quickly but has a slow cluster startup can still miss its
SLA if startup time isn't accounted for.
