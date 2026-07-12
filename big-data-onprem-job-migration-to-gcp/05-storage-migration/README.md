# 05 — Storage Migration (HDFS → GCS)

## Purpose

Move the data itself — not yet the jobs that process it — from HDFS to the
GCS bucket structure designed in
[`04-target-architecture/04-storage-architecture.md`](../04-target-architecture/04-storage-architecture.md).
This phase is deliberately sequenced before
[`07-spark-migration/`](../07-spark-migration/README.md): data needs to
exist in GCS before migrated jobs can be validated against it, and running
storage migration as its own phase (rather than bundled into each job's
migration) lets it be validated, checksummed, and de-risked independently.

## Owner

**Platform Engineering / Cloud-DevOps**, executed per data domain in the
order determined by
[`14-job-migration/`](../14-job-migration/README.md) wave sequencing (a
data domain's storage migration must precede or accompany the first wave
that needs it — it does not need to happen for the whole platform at once).

## Inputs

- Storage inventory from
  [`01-discovery/inventories/11-storage-inventory.md`](../01-discovery/inventories/11-storage-inventory.md)
  (volume, ownership, growth rate per HDFS path).
- Target GCS bucket structure from
  [`04-target-architecture/04-storage-architecture.md`](../04-target-architecture/04-storage-architecture.md).
- Network connectivity from [`11-network/`](../11-network/README.md)
  (bandwidth available for transfer).
- Retention/compliance requirements from
  [`01-discovery/inventories/04-data-retention-and-compliance.md`](../01-discovery/inventories/04-data-retention-and-compliance.md).

## Outputs

- Every in-scope HDFS directory replicated to its target GCS location,
  checksummed and validated.
- A documented, tested incremental sync mechanism for keeping GCS current
  during the parallel-run period before each job's cutover.
- Permissions/ownership mapped from HDFS ACLs to the IAM design in
  [`10-security/`](../10-security/README.md).

## Prerequisites

[`04-target-architecture/`](../04-target-architecture/README.md) gated
(bucket structure must be final); network connectivity between on-prem and
GCP established per [`11-network/`](../11-network/README.md) (at least a
non-production path, sufficient for pilot-domain migration).

## Deliverables

1. Migration strategy per data domain (DistCp vs. Storage Transfer Service
   vs. hybrid), with rationale.
2. Executable, tested runbooks for both DistCp and Storage Transfer
   Service paths.
3. An incremental sync mechanism for the parallel-run window.
4. A checksum-based validation procedure, run and passed for every
   migrated data domain.
5. A permissions/metadata mapping from HDFS ACLs/Ranger policies to GCS
   IAM.
6. A tested rollback procedure.

## Risks

- **Silent data corruption during transfer** — mitigated exclusively
  through the checksum validation procedure in
  [`05-checksum-and-validation.md`](05-checksum-and-validation.md); no
  data domain is considered migrated without it passing.
- **Transfer time exceeding available maintenance/off-peak windows** for
  very large data domains — sized explicitly per domain using the volume
  data in
  [`01-discovery/inventories/11-storage-inventory.md`](../01-discovery/inventories/11-storage-inventory.md)
  before committing to a wave schedule.
- **Incremental sync falling behind** during an extended parallel-run
  period, causing validation against stale GCS data — monitored explicitly,
  see [`04-incremental-sync-strategy.md`](04-incremental-sync-strategy.md).

## Rollback

Every data domain's migration has an explicit rollback path — see
[`07-rollback-procedure.md`](07-rollback-procedure.md). Because the
on-prem HDFS data is never deleted until
[`22-hypercare/`](../22-hypercare/README.md) confirms stability, rollback
for this phase is low-risk: it means reverting job configuration to read
from HDFS again, not restoring lost data.

## Validation

No data domain is marked migrated until it passes 100% checksum validation
against its HDFS source (see
[`05-checksum-and-validation.md`](05-checksum-and-validation.md)) and a
manual spot-check by the owning data engineering team.

## Best Practices

Migrate and validate the **lowest-risk, smallest data domain first** as a
pilot — this proves the runbook end-to-end (including the parts that are
hard to fully test without real execution: actual transfer throughput,
actual checksum mismatch handling) before committing to Tier 1 domains.

## Lessons Learned

Underestimating replication-factor-adjusted transfer volume (see
[`01-discovery/inventories/11-storage-inventory.md`](../01-discovery/inventories/11-storage-inventory.md)
"effective unique data volume" note) is the most common cause of storage
migration timeline overruns — always plan against effective volume, not
raw HDFS "used" capacity.

## Common Mistakes

- Treating storage migration as "just a copy" and skipping checksum
  validation for "obviously fine" small domains — corruption risk is not
  proportional to data size.
- Migrating permissions as an afterthought instead of mapping them
  deliberately to the new IAM model in
  [`10-security/`](../10-security/README.md) — see
  [`06-permissions-and-metadata-migration.md`](06-permissions-and-metadata-migration.md).

## Production Notes

Schedule bulk transfer activity for Tier 1 data domains during the
lowest-utilization windows identified in
[`01-discovery/inventories/03-peak-hours-and-downtime-windows.md`](../01-discovery/inventories/03-peak-hours-and-downtime-windows.md)
to avoid competing with production on-prem workloads for network/disk I/O
during transfer.

---

## Folder structure

```
05-storage-migration/
├── README.md                                       This file
├── 01-migration-strategy-overview.md                DistCp vs. STS decision per data domain
├── 02-distcp-migration-procedure.md                 Executable DistCp runbook
├── 03-storage-transfer-service-procedure.md         Executable STS runbook
├── 04-incremental-sync-strategy.md                  Keeping GCS current during parallel-run
├── 05-checksum-and-validation.md                    Validation methodology
├── 06-permissions-and-metadata-migration.md          HDFS ACL → GCS IAM mapping
├── 07-rollback-procedure.md                          Tested rollback path
└── 08-migration-execution-checklist.md               Per-domain execution checklist template
```
