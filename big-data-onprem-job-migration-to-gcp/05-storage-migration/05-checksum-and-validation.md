# Checksum & Validation Procedure

**Purpose:** Define the mandatory, non-negotiable procedure for proving a
storage migration transferred data correctly and completely — the gate
every data domain must pass before being considered migrated. This is the
storage-layer counterpart to the broader data validation framework in
[`16-data-validation/`](../16-data-validation/README.md), scoped
specifically to "did the bytes move correctly," not "is the data
business-correct" (which is a separate, later concern).
**Owner:** Platform Engineering, results reviewed by the data domain's
owning Data Engineering team.

---

## Validation levels

| Level | What It Checks | Method |
|---|---|---|
| **1. File count and size** | Every file present in source is present in target, with matching size | `hdfs dfs -count` vs. `gsutil du` comparison, or `gcloud transfer operations describe` summary for STS |
| **2. Checksum comparison** | File content is byte-identical, not just same size | See procedure below |
| **3. Sample-based content spot-check** | Data is readable and structurally valid in the new location (not just byte-identical, but actually openable/queryable) | Load a sample of migrated Parquet/ORC files via Spark/BigQuery and confirm schema and row count match a source-side read |
| **4. Row/record count reconciliation** (for structured data) | Aggregate record counts match between source and target | Compare `SELECT COUNT(*)` (or equivalent) between the source Hive table and a query against the migrated GCS-backed table |

All four levels are required for Tier 1 data domains. Levels 1, 2, and 4
are required for all domains; level 3 is strongly recommended for all and
mandatory for any domain feeding a Tier 1 job.

## Checksum comparison procedure

HDFS and GCS do not share a native checksum algorithm by default (HDFS
uses CRC32C internally per block; GCS uses CRC32C or MD5 depending on
object composition), so validation uses a comparable, independently
computed checksum on both sides:

```bash
# On HDFS side — compute a whole-file checksum
hdfs dfs -checksum /data/<domain>/<file> > hdfs_checksums.txt

# On GCS side — compute the equivalent checksum
gsutil hash -c gs://<company>-<env>-<domain>-raw/<file> > gcs_checksums.txt
```

For DistCp-transferred data, `-Dfs.gs.checksum.type=CRC32C` combined with
HDFS's own CRC32C block checksums allows a more direct comparison — confirm
compatibility for the specific Hadoop/connector version in use, and where
native checksum algorithms don't align cleanly, fall back to an
independent content hash comparison (e.g., `md5sum` on both sides for a
sampled or complete file set, depending on data volume).

## Automated validation script pattern

Do not perform this validation manually per file for any non-trivial
domain. Build a scripted comparison (see
[`scripts/`](../scripts/README.md) for the reusable version of this
pattern) that:

1. Lists all files/objects on both source and target.
2. Compares file count and total size.
3. Computes and compares checksums for every file (or a statistically
   significant sample for very large domains, with 100% coverage required
   for Tier 1).
4. Outputs a pass/fail report with any mismatched or missing files
   explicitly listed.
5. Is re-runnable safely (idempotent) so it can be re-executed after fixing
   any discovered discrepancy.

## Handling validation failures

| Failure Type | Likely Cause | Resolution |
|---|---|---|
| Missing files in target | Transfer interrupted or filtered incorrectly | Re-run transfer with `-update`/`--overwrite-when=different`; do not assume it's safe to ignore a small gap |
| Size mismatch | Partial/corrupted transfer | Re-transfer the specific file(s); investigate root cause if recurring |
| Checksum mismatch, matching size | Silent corruption during transfer (rare but must be caught) | Re-transfer; escalate if recurring across multiple files, which may indicate a connector or network-layer issue |
| Row count mismatch (structured data) | Could indicate corruption, or could indicate legitimate concurrent writes during transfer if incremental sync wasn't running | Confirm timing against the source; re-validate after ensuring sync is current |

## Sign-off

| Field | Requirement |
|---|---|
| Validation report reviewed by | Data Engineering (domain owner) |
| Validation report reviewed by | Platform Engineering |
| Sign-off recorded in | [`14-job-migration/`](../14-job-migration/README.md) tracker, against the relevant job/domain entry |

## Common Mistakes

- Sampling checksum validation for a Tier 1 domain instead of full
  coverage — sampling is acceptable for lower-tier, very large domains,
  but not for business-critical data.
- Treating a passed file-count/size check as sufficient without a
  checksum-level comparison — matching size does not prove matching
  content.

## Production Notes

For domains feeding Tier 1 jobs, run the row/record count reconciliation
(Level 4) against a live, non-cached read from both source and target at
the same logical point in time (i.e., pause writes briefly or compare
against a known-consistent snapshot) — comparing counts across two systems
that are actively being written to independently produces false-positive
mismatches unrelated to actual data integrity.
