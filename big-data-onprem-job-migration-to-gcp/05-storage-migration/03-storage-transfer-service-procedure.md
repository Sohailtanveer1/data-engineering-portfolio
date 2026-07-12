# Storage Transfer Service Procedure

**Purpose:** An executable runbook for using GCP's Storage Transfer
Service (STS), agent-based mode, to migrate a data domain from HDFS to GCS
without consuming on-prem Hadoop cluster compute resources for the
transfer itself.
**Owner:** Platform Engineering / Cloud-DevOps.
**Prerequisites:** Network connectivity from on-prem to GCP per
[`11-network/`](../11-network/README.md); target GCS bucket created via
Terraform per [`13-infrastructure/`](../13-infrastructure/README.md);
sufficient on-prem host(s) available to run the STS agent (a lightweight
Docker-based agent, not a Hadoop cluster job).

---

## Step-by-step procedure

### 1. Deploy the STS on-prem agent pool

Deploy the STS agent on one or more dedicated (non-Hadoop-cluster) hosts
with network access to both HDFS (as an NFS-mounted or HDFS-accessible
source, per STS's on-prem source requirements) and the internet/GCP API
endpoint:

```bash
docker run -d --name sts-agent \
  --network=host \
  gcr.io/cloud-ingest/tsop-agent:latest \
  --project-id=<gcp-project-id> \
  --hostname=<on-prem-agent-hostname> \
  --creds-file=/path/to/sts-service-account-key.json \
  --agent-pool=<agent-pool-name>
```

Deploy multiple agent instances (an "agent pool") for higher throughput and
redundancy — a single-agent deployment is a transfer-speed bottleneck and a
single point of failure for a Tier 1 domain's migration.

### 2. Create the transfer job

Via `gcloud` (preferred for repeatability/auditability over the Console
UI):

```bash
gcloud transfer jobs create \
  posix://<on-prem-source-path-exposed-to-agent>/data/<domain>/ \
  gs://<company>-<env>-<domain>-raw/ \
  --source-agent-pool=<agent-pool-name> \
  --name=transfer-<domain>-<env> \
  --description="Bulk migration of <domain> from HDFS to GCS"
```

Note: STS's on-prem source connector reads from a POSIX-compatible
filesystem view, not HDFS's native RPC protocol directly — confirm the
source path is exposed via an NFS gateway (e.g., HDFS NFS Gateway) or
equivalent POSIX-accessible mount before configuring the transfer job; this
is a key architectural difference from DistCp, which speaks HDFS natively.

### 3. Configure incremental sync scheduling (if using STS for ongoing sync)

```bash
gcloud transfer jobs update transfer-<domain>-<env> \
  --schedule-starts=2026-07-15 \
  --schedule-repeats-every=1d \
  --overwrite-when=different
```

`--overwrite-when=different` ensures only changed files are re-transferred
on each scheduled run — see
[`04-incremental-sync-strategy.md`](04-incremental-sync-strategy.md) for
the full incremental sync design.

### 4. Monitor the transfer

```bash
gcloud transfer operations list --job-names=transfer-<domain>-<env>
gcloud transfer operations describe <operation-id>
```

Also visible in Cloud Console under Storage Transfer Service, and
integrated with Cloud Monitoring per
[`18-monitoring/`](../18-monitoring/README.md) for alerting on transfer
failures.

### 5. Post-transfer verification

Proceed to [`05-checksum-and-validation.md`](05-checksum-and-validation.md)
— STS's built-in integrity checks are a first check, not a substitute for
the independent checksum validation procedure.

### 6. Log the execution

Record in [`logs/`](../logs/README.md) as with the DistCp procedure.

## Common Mistakes

- Assuming STS can read HDFS directly without an intermediate POSIX-
  compatible exposure (e.g., HDFS NFS Gateway) — this is a common
  misunderstanding that blocks setup if not planned for in advance.
- Running a single-agent pool for a large Tier 1 domain, creating both a
  throughput bottleneck and a single point of failure for the transfer
  itself.
- Leaving a scheduled incremental sync job running indefinitely after a
  job's wave has fully cut over and the parallel-run period has ended —
  clean up completed transfer job schedules to avoid unnecessary ongoing
  cost and confusion about which sync jobs are still load-bearing.

## Production Notes

For Tier 1 domains using STS for incremental sync during an extended
parallel-run window, configure Cloud Monitoring alerts (per
[`18-monitoring/`](../18-monitoring/README.md)) on transfer job failure or
delay specifically — a silently failing incremental sync during
parallel-run means validation in
[`16-data-validation/`](../16-data-validation/README.md) is unknowingly
comparing against stale GCS data.
