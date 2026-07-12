# DistCp Migration Procedure

**Purpose:** An executable, step-by-step runbook for using Hadoop DistCp
with the GCS connector to bulk-transfer a data domain from HDFS to GCS.
**Owner:** Platform Engineering (executor), reviewed by the data domain's
owning team before execution.
**Prerequisites:** GCS connector for Hadoop installed on the cluster
(`gcs-connector-hadoop3-<version>.jar` or equivalent for the cluster's
Hadoop version); a GCP service account with write access to the target
bucket, its key or Workload Identity Federation configured on the cluster;
target GCS bucket already created via Terraform per
[`13-infrastructure/`](../13-infrastructure/README.md).

---

## Step-by-step procedure

### 1. Pre-flight checks

```bash
# Confirm source path size and file count (effective, not replicated)
hdfs dfs -count -q -h /data/<domain>/

# Confirm GCS connector is available on the cluster
hadoop classpath | grep -i gcs-connector

# Confirm target bucket is reachable and the service account has access
gsutil ls gs://<company>-<env>-<domain>-raw/
```

Record the source file count and size — this is the baseline the
post-transfer validation in
[`05-checksum-and-validation.md`](05-checksum-and-validation.md) confirms
against.

### 2. Configure the GCS connector (if not already cluster-wide)

Ensure `core-site.xml` (or a job-specific config override) includes:

```xml
<property>
  <name>fs.gs.impl</name>
  <value>com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem</value>
</property>
<property>
  <name>google.cloud.auth.service.account.enable</name>
  <value>true</value>
</property>
<property>
  <name>google.cloud.auth.service.account.json.keyfile</name>
  <value>/path/to/distcp-service-account-key.json</value>
</property>
```

Treat the service account key file as a secret — restrict filesystem
permissions to the executing user only, and rotate/revoke it immediately
after the migration phase completes, consistent with the least-privilege
principle in
[`04-target-architecture/07-security-architecture-overview.md`](../04-target-architecture/07-security-architecture-overview.md).

### 3. Run a dry run on a small subdirectory first

```bash
hadoop distcp -dryrun \
  hdfs:///data/<domain>/dt=2026-07-01/ \
  gs://<company>-<env>-<domain>-raw/dt=2026-07-01/
```

Confirm the dry-run plan matches expectations (file count, no unexpected
skips) before running against the full domain.

### 4. Execute the bulk transfer

```bash
hadoop distcp \
  -Dmapreduce.job.queuename=<migration-queue> \
  -pb \
  -update \
  -m <number-of-mappers, sized to available off-peak capacity> \
  hdfs:///data/<domain>/ \
  gs://<company>-<env>-<domain>-raw/
```

Flag reference:
- `-pb` preserves block size (informational only for GCS, since GCS has no
  block concept, but keeps metadata consistent for later analysis).
- `-update` — only copies files that are new or changed, making this
  command safely re-runnable (also the basis for a lightweight incremental
  sync if STS is not used — see
  [`04-incremental-sync-strategy.md`](04-incremental-sync-strategy.md)).
- `-m` — cap mapper count to avoid saturating cluster network capacity
  during production hours; run during the off-peak windows identified in
  [`01-discovery/inventories/03-peak-hours-and-downtime-windows.md`](../01-discovery/inventories/03-peak-hours-and-downtime-windows.md).

### 5. Post-transfer verification

Proceed immediately to
[`05-checksum-and-validation.md`](05-checksum-and-validation.md) — a
DistCp run is not considered complete until checksum validation passes.

### 6. Log the execution

Record in [`logs/`](../logs/README.md): domain migrated, start/end time,
file count transferred, any errors/retries encountered, and the checksum
validation result.

## Common Mistakes

- Running DistCp without `-update` on a re-run, causing unnecessary
  re-transfer of unchanged files and wasted time/bandwidth.
- Not capping mapper count (`-m`), causing DistCp to consume enough
  cluster network/compute capacity to visibly degrade concurrent
  production job performance — coordinate the mapper count and run window
  with Platform Engineering ahead of time, especially for Tier 1 domains.
- Forgetting to revoke/rotate the migration service account key after the
  transfer completes, leaving an unnecessarily broad credential active
  longer than needed.

## Production Notes

For Tier 1 domains, run the transfer in visible communication with the
on-call/operations team (per
[`01-discovery/questions/07-operations.md`](../01-discovery/questions/07-operations.md))
so any unexpected cluster load during the transfer window is immediately
attributable and not mistaken for a production incident.
