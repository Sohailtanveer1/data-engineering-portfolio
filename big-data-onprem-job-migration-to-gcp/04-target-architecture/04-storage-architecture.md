# Storage Architecture

**Purpose:** Define the GCS bucket structure, storage class strategy, and
data zoning model that
[`05-storage-migration/`](../05-storage-migration/README.md) migrates data
into and that all Spark/Composer jobs read from and write to.
**Owner:** Platform Engineering + Cloud/DevOps, reviewed by Security for
access control implications.

---

## Data zoning model

| Zone | Purpose | Storage Class | Retention/Lifecycle |
|---|---|---|---|
| **Raw / Landing** | Immutable copy of data as received (from HDFS migration or new ingestion) — never modified after write | Standard | Lifecycle-managed transition to Nearline after N days per data domain, see [`01-discovery/inventories/04-data-retention-and-compliance.md`](../01-discovery/inventories/04-data-retention-and-compliance.md) |
| **Curated** | Cleaned, validated, business-logic-applied data — the output of Spark transformation jobs | Standard | Active window per retention policy; transitions to Nearline/Coldline per data domain schedule |
| **Archive** | Data past its active-use window but within compliance retention | Coldline / Archive | Governed strictly by [`01-discovery/inventories/04-data-retention-and-compliance.md`](../01-discovery/inventories/04-data-retention-and-compliance.md); deleted only via an explicit, audited process at true retention expiry |
| **Scratch / Temp** | Spark job intermediate/shuffle-adjacent temp data | Standard, short lifecycle (e.g., 7-day auto-delete) | Never relied upon beyond a single job run |

This raw → curated → archive zoning directly maps to the target
architecture diagram in
[`01-target-architecture-overview.md`](01-target-architecture-overview.md)
and gives every job a predictable, consistent place to read from and write
to — replacing the ad-hoc HDFS directory conventions documented in
[`01-discovery/inventories/11-storage-inventory.md`](../01-discovery/inventories/11-storage-inventory.md).

## Bucket structure

Following the naming convention in
[`02-landing-zone-and-project-structure.md`](02-landing-zone-and-project-structure.md):

```
gs://<company>-<env>-<data-domain>-raw/
gs://<company>-<env>-<data-domain>-curated/
gs://<company>-<env>-<data-domain>-archive/
gs://<company>-<env>-scratch/            (shared, short-lived, not per-domain)
```

Example, for the `pricing` data domain in `prod`:

```
gs://acme-prod-pricing-raw/
gs://acme-prod-pricing-curated/
gs://acme-prod-pricing-archive/
```

**One bucket set per data domain**, not one giant bucket for the whole
platform — this makes IAM scoping (per
[`10-security/`](../10-security/README.md)), cost attribution (per
[`19-cost-optimization/`](../19-cost-optimization/README.md)), and
lifecycle policy management all cleanly separable per team/domain,
mirroring the HDFS directory-per-domain structure already in use today
(see
[`01-discovery/inventories/11-storage-inventory.md`](../01-discovery/inventories/11-storage-inventory.md))
rather than introducing an unfamiliar new mental model.

## Object naming / partitioning convention

Carry forward Hive-style partition-friendly path structure to keep
external table definitions and query pruning behavior familiar:

```
gs://acme-prod-pricing-curated/daily_price_snapshot/dt=2026-07-12/part-00000.parquet
```

## File format standard

**Parquet is the default target format** for all curated-zone data,
consistent with the majority-Parquet finding in
[`01-discovery/inventories/09-hive-inventory.md`](../01-discovery/inventories/09-hive-inventory.md).
Legacy text/CSV/SequenceFile-format tables are explicitly converted during
[`06-data-migration/`](../06-data-migration/README.md), not carried
forward as-is — this both resolves pain point #5 (legacy format storage
cost) from
[`03-current-environment/09-pain-points-and-bottlenecks.md`](../03-current-environment/09-pain-points-and-bottlenecks.md)
and improves BigQuery/Dataproc query performance uniformly.

## Encryption

All buckets use **Customer-Managed Encryption Keys (CMEK)** via Cloud KMS
for any data domain classified Restricted or Confidential per
[`01-discovery/inventories/04-data-retention-and-compliance.md`](../01-discovery/inventories/04-data-retention-and-compliance.md).
Full key management design is in
[`10-security/`](../10-security/README.md).

## Regional strategy

| Consideration | Decision |
|---|---|
| Single-region vs. dual-region/multi-region buckets | Determined per data domain by the required RTO/RPO in [`01-discovery/inventories/05-disaster-recovery-rpo-rto.md`](../01-discovery/inventories/05-disaster-recovery-rpo-rto.md) — Tier 1 domains default to dual-region for resilience; lower tiers default to single-region for cost efficiency |
| Region selection | Aligned with data residency constraints from [`01-discovery/questions/03-security-team.md`](../01-discovery/questions/03-security-team.md) Q7 and proximity to the primary Dataproc/Composer region for latency/egress cost |

## Common Mistakes

- Creating one monolithic bucket for the entire platform — this makes
  fine-grained IAM and cost attribution far harder than the equivalent
  per-domain bucket structure, and doesn't match how the current HDFS
  structure (and therefore existing tooling/scripts/mental models) is
  already organized.
- Migrating data into GCS without addressing legacy format conversion,
  simply reproducing the current-state format inefficiency on a new
  platform.

## Production Notes

For Tier 1 data domains, confirm the dual-region bucket decision explicitly
against the RTO/RPO targets in
[`01-discovery/inventories/05-disaster-recovery-rpo-rto.md`](../01-discovery/inventories/05-disaster-recovery-rpo-rto.md)
— don't default to single-region for cost savings on a domain where the
business has stated a low RTO/RPO tolerance.
