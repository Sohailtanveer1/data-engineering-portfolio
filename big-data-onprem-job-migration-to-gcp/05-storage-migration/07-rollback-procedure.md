# Rollback Procedure — Storage Migration

**Purpose:** Define exactly how to revert if a data domain's storage
migration is found to be incomplete, corrupted, or otherwise unsafe to
proceed on, after some downstream work (job migration, validation) has
already begun depending on it.
**Owner:** Platform Engineering, decision authority per RACI
([`00-project-overview/03-raci-matrix.md`](../00-project-overview/03-raci-matrix.md)) —
Migration Program Lead is Accountable for the rollback decision.

---

## Why storage-migration rollback is inherently low-risk

Per constraint C7
([`00-project-overview/06-assumptions-and-constraints.md`](../00-project-overview/06-assumptions-and-constraints.md)),
the on-prem HDFS source is **never deleted or modified** as part of this
phase — storage migration is purely additive (data is copied to GCS, not
moved or removed from HDFS) until
[`22-hypercare/`](../22-hypercare/README.md) explicitly confirms stability
and a separate, deliberate decommissioning step occurs. This means
rollback for this phase never involves "restoring lost data" — the
authoritative source is always still on-prem.

## Rollback triggers

| Trigger | Action |
|---|---|
| Checksum validation fails and cannot be resolved by re-transfer | Do not proceed to job cutover for the affected domain; jobs continue reading from HDFS as before |
| Incremental sync falls significantly and unrecoverably behind during parallel-run | Pause validation activity relying on the GCS copy; jobs continue reading from HDFS; investigate and re-sync before resuming |
| IAM/permissions mapping found to have widened access inappropriately (post-migration discovery) | Immediately restrict the offending IAM binding; audit access logs for the exposure window; do not wait for the next scheduled review |
| Post-cutover data quality issue traced back to a storage migration defect (discovered during hypercare) | See the job-level rollback procedure in [`21-cutover/`](../21-cutover/README.md) — this may require reverting the job's read path back to HDFS temporarily while the GCS copy is corrected |

## Rollback steps

### If rollback is needed before job cutover (most common case)

1. No action needed on the job side — jobs are still reading from HDFS.
2. Investigate and fix the root cause of the storage migration issue.
3. Re-run the migration procedure
   ([`02-distcp-migration-procedure.md`](02-distcp-migration-procedure.md)
   or
   [`03-storage-transfer-service-procedure.md`](03-storage-transfer-service-procedure.md))
   for the affected domain.
4. Re-run validation
   ([`05-checksum-and-validation.md`](05-checksum-and-validation.md))
   before attempting cutover again.

### If rollback is needed after job cutover (during hypercare)

This is a job-level rollback, not purely a storage-level one — coordinate
with [`21-cutover/`](../21-cutover/README.md) and
[`22-hypercare/`](../22-hypercare/README.md) rollback procedures:

1. Revert the job's Composer DAG/configuration to read from HDFS again
   (only possible if the on-prem job/scheduler entry has not yet been
   decommissioned — see the decommissioning gate below).
2. Investigate and fix the GCS-side data issue.
3. Re-validate before attempting cutover again.
4. Document the incident in
   [`logs/`](../logs/README.md) and feed lessons learned back into
   [`documentation/`](../documentation/README.md).

## Decommissioning gate — when rollback stops being an option

The on-prem source for a given data domain is only decommissioned (or the
corresponding on-prem job/scheduler entry removed) after:

1. [`22-hypercare/`](../22-hypercare/README.md) stabilization period is
   complete with no unresolved issues for that domain's jobs.
2. Explicit sign-off from the Migration Program Lead.

Until that gate is passed, rollback per this document remains available.
This gate is the boundary between "storage migration rollback is trivial"
and "storage migration rollback requires the full cutover rollback
process."

## Common Mistakes

- Decommissioning on-prem HDFS paths or jobs prematurely (e.g., to "clean
  up" or reclaim capacity) before the hypercare gate is passed — this
  removes the rollback safety net the entire migration strategy depends on.
- Treating a failed validation as a reason to force through the migration
  anyway "since we're behind schedule" — a failed checksum validation is a
  hard stop, not a risk to be accepted informally.

## Production Notes

For Tier 1 domains, explicitly confirm with Business Owners
(per the RACI) before decommissioning any on-prem source — even after
hypercare sign-off, some business functions may have a compliance or
audit reason to want the on-prem copy retained slightly longer than the
standard gate requires.
