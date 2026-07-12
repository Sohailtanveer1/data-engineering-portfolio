# Snapshot Strategy

**Purpose:** Define how point-in-time snapshots are taken and used during
migration — both as a reconciliation reference point (comparing source and
target at a known-consistent moment) and as a rollback safety net
independent of the ongoing incremental/CDC pipelines.
**Owner:** Data Engineering.

---

## Why snapshots matter during migration specifically

Both the source (on-prem Hive/HDFS) and target (BigQuery/GCS) are live
systems being written to continuously during the migration program. Any
reconciliation comparison
([`07-data-reconciliation-framework.md`](07-data-reconciliation-framework.md))
between two continuously-changing systems is only meaningful if both sides
are compared **as of the same logical point in time** — otherwise
legitimate in-flight writes are indistinguishable from real discrepancies.
Snapshots solve this.

## Snapshot mechanism per source type

| Source | Snapshot Mechanism |
|---|---|
| Hive external table (Parquet/ORC on HDFS) | Partition-based: snapshot = the set of partitions as of a specific `dt`/`hour` value, since new partitions don't retroactively modify old ones |
| Hive managed table with in-place updates (less common but possible) | Requires a coordinated pause of writes, or a Hive/HDFS-level point-in-time copy (e.g., `distcp` snapshot of a specific HDFS snapshot if HDFS snapshotting is enabled) |
| BigQuery target table | BigQuery table snapshots (native feature) — cheap, fast, and directly comparable |
| GCS curated zone | Object versioning (if enabled) or a partition-based snapshot equivalent to the Hive approach |

## Recommended: leverage HDFS snapshots where available

If HDFS snapshotting is enabled on the source cluster (confirm in
[`03-current-environment/01-hadoop-cluster-assessment.md`](../03-current-environment/01-hadoop-cluster-assessment.md)),
use `hdfs dfs -createSnapshot` to create a consistent, point-in-time,
storage-efficient reference copy of a directory before running
reconciliation — this avoids the need to pause writes for tables that
otherwise would require it.

```bash
hdfs dfsadmin -allowSnapshot /data/<domain>/
hdfs dfs -createSnapshot /data/<domain>/ migration-recon-<date>
```

## Snapshot usage points in the migration lifecycle

1. **Pre-backfill baseline snapshot** — taken immediately before historical
   backfill begins, giving a stable reference for
   [`01-historical-data-migration-plan.md`](01-historical-data-migration-plan.md)
   batch reconciliation.
2. **Pre-cutover snapshot** — taken immediately before a job's final
   cutover in [`14-job-migration/`](../14-job-migration/README.md), giving
   a clean rollback reference point independent of whatever incremental
   sync state exists at that moment.
3. **Periodic reconciliation snapshots** — taken on a schedule during
   extended parallel-run periods (e.g., weekly) to catch drift early rather
   than only at final cutover.

## Snapshot retention

Migration-specific snapshots are retained through the
[`22-hypercare/`](../22-hypercare/README.md) stabilization period, then
cleaned up — they are a migration safety mechanism, not a permanent
backup/DR solution (that's addressed separately in
[`01-discovery/inventories/05-disaster-recovery-rpo-rto.md`](../01-discovery/inventories/05-disaster-recovery-rpo-rto.md)
and the target architecture's regional/replication design).

## Common Mistakes

- Running reconciliation comparisons against live, continuously-changing
  source and target without a snapshot reference — this produces noisy,
  hard-to-interpret false-positive discrepancies caused entirely by timing,
  not real data issues.
- Leaving migration snapshots in place indefinitely after hypercare,
  accumulating unnecessary storage cost — clean up on a defined schedule.

## Production Notes

For Tier 1 tables, take the pre-cutover snapshot as close to the actual
cutover moment as operationally practical (per
[`21-cutover/`](../21-cutover/README.md) sequencing) to minimize the
window of legitimate source changes that occur between the snapshot and
the actual cutover moment.
