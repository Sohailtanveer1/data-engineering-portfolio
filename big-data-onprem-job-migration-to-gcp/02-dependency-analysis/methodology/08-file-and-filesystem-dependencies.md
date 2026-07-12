# Identifying File Transfer & Filesystem Dependencies (FTP/SFTP/NFS/HDFS)

**Purpose:** Group together the filesystem- and file-transfer-based
dependency categories (FTP, SFTP, NFS, and internal HDFS path dependencies
not already captured as job read/write paths) since they share a common
discovery technique: finding mount points, transfer commands, and path
references in scripts and configuration.
**Owner:** Platform Engineering.
**Inputs:** `/etc/fstab` and mount configuration on every relevant node,
SFTP/FTP client configuration and scripts, HDFS path references outside of
Spark job code (e.g., in shell scripts or Hive external table locations).

---

## What to look for — FTP/SFTP

1. **Every SFTP/FTP client invocation** in shell scripts — target host,
   authentication method (key-based vs. password), directory paths used,
   and whether the script is pulling (inbound) or pushing (outbound) files.
2. **Scheduled vs. triggered transfers** — is the transfer on a fixed
   schedule, or triggered by a file-arrival watcher/polling script?
3. **File naming and archival conventions** — how are processed files
   distinguished from unprocessed ones (renaming, moving to an archive
   subdirectory, deletion)? This logic must be preserved or deliberately
   redesigned, not silently dropped.

## What to look for — NFS

1. **Every NFS mount** referenced in `/etc/fstab` or mounted at runtime on
   edge nodes or (unusually, but it happens) worker nodes.
2. **What's stored on the NFS mount** — commonly shared reference data,
   lookup tables, or shared configuration used across many jobs. This is
   architecturally significant: Dataproc worker nodes are ephemeral and
   should not depend on a persistent NFS mount, so every NFS dependency
   found here needs an explicit GCS-based redesign in
   [`07-spark-migration/`](../../07-spark-migration/README.md), not a
   lift-and-shift.

## What to look for — Internal HDFS Path Dependencies

1. **Hive external table `LOCATION` clauses** pointing at HDFS paths not
   already captured via job-level read/write analysis in
   [`01-spark-job-dependencies.md`](01-spark-job-dependencies.md).
2. **Hardcoded HDFS paths in shell scripts** performing direct
   `hdfs dfs -cp`/`-mv`/`-rm` operations outside of any Spark job — these
   are common for "staging area" cleanup or archival scripts and are easy
   to miss since they aren't part of any job's core logic.
3. **HDFS ACL and quota configuration** per top-level directory, which
   informs the GCS IAM design in
   [`10-security/`](../../10-security/README.md).

## Technique

1. **Mount and fstab sweep.** Across every edge, gateway, and (if
   applicable) worker node, collect `/etc/fstab` and active `mount` output;
   cross-reference NFS mount points against the storage inventory in
   [`01-discovery/inventories/11-storage-inventory.md`](../../01-discovery/inventories/11-storage-inventory.md).
2. **Script-level grep.** Search all shell scripts for `sftp`, `ftp`,
   `scp`, `hdfs dfs`, and mount-path literals.
3. **Hive Metastore location extraction.** Query the Metastore for every
   external table's `LOCATION` and cross-reference against known job read
   paths — any location with no corresponding job/consumer identified in
   [`02-hive-dependencies.md`](02-hive-dependencies.md) is a gap requiring
   investigation.
4. **File arrival pattern documentation.** For every inbound
   FTP/SFTP feed, document the actual arrival cadence and any observed
   irregularity (late files, missing files, out-of-order arrival) — these
   real-world patterns must be handled by the redesigned Composer sensor
   logic in [`09-composer-migration/`](../../09-composer-migration/README.md),
   not just the documented/expected cadence.

## Output format

Add findings to
[`01-discovery/inventories/12-external-dependencies.md`](../../01-discovery/inventories/12-external-dependencies.md)
(FTP/SFTP entries) and
[`01-discovery/inventories/11-storage-inventory.md`](../../01-discovery/inventories/11-storage-inventory.md)
(NFS and internal HDFS path entries).

## Common Mistakes

- Assuming NFS-mounted reference data is small and can be "handled later"
  — reference/lookup data dependencies are exactly the kind of thing that
  silently breaks every job depending on them if migrated carelessly or
  late.
- Missing FTP/SFTP transfers configured via a scheduled task on a
  Windows-based edge system if the estate has any non-Linux components —
  don't assume every transfer mechanism lives on a Linux cron job.

## Production Notes

Every partner-facing SFTP integration needs explicit advance coordination
(see the "Production Notes" in
[`01-discovery/inventories/12-external-dependencies.md`](../../01-discovery/inventories/12-external-dependencies.md))
— changing an SFTP endpoint or host key without vendor notice is a common,
entirely avoidable cause of a broken partner integration at cutover.
