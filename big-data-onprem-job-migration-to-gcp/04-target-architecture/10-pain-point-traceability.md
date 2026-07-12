# Pain Point Traceability Matrix

**Purpose:** Force an explicit, checkable link between every "High"
severity pain point identified in
[`03-current-environment/09-pain-points-and-bottlenecks.md`](../03-current-environment/09-pain-points-and-bottlenecks.md)
and the specific architectural decision in this folder that resolves it —
or an explicit, signed-off statement that it is consciously deferred. This
is what proves the target architecture was designed against this
platform's real problems, not assembled from generic best practices.
**Owner:** Migration Program Lead.
**Validation:** Every row with "Resolved: No" must have an explicit
sign-off from the Executive Sponsor before this folder can be gated —
silently shipping an unresolved High-severity pain point is not acceptable.

---

## Traceability matrix

| Pain Point (from current-environment assessment) | Severity | Resolved By | Document Reference | Resolved? |
|---|---|---|---|---|
| #1 Fixed hardware capacity forces over/under-provisioning | High | Ephemeral, autoscaled Dataproc clusters | [`03-compute-architecture.md`](03-compute-architecture.md) | Yes |
| #2 Single, non-HA NameNode/Metastore SPOF | High | Managed GCS (11 nines durability) + Dataproc Metastore (managed HA) | [`04-storage-architecture.md`](04-storage-architecture.md), [`05-data-warehouse-architecture.md`](05-data-warehouse-architecture.md) | Yes |
| #3 Queue contention causes job delays | Medium-High | Ephemeral per-job clusters eliminate shared-queue contention entirely | [`03-compute-architecture.md`](03-compute-architecture.md) | Yes |
| #4 Hardware nearing/past end-of-life | Medium | Migration itself removes dependency on the physical hardware | N/A — resolved by program completion, not a specific architecture doc | Yes (indirectly) |
| #5 Legacy text/CSV format tables — storage/query cost | Medium | Standardization on Parquet during data migration | [`04-storage-architecture.md`](04-storage-architecture.md) | Yes |
| #6 No tested DR/backup restore process | High | Explicit RTO/RPO-driven regional strategy + managed service DR characteristics | [`04-storage-architecture.md`](04-storage-architecture.md) regional strategy section | Yes — validated by testing in [`15-testing/`](../15-testing/README.md) |
| #7 Manual, undocumented operational interventions | Medium | Idempotency and retry-logic redesign requirement | Carried forward to [`07-spark-migration/`](../07-spark-migration/README.md) — not resolved by architecture alone, requires execution-phase discipline | Partial — architecture enables it, execution must deliver it |
| #8 Client-mode Spark jobs with edge-node-local dependencies | Medium | Standardized cluster-mode Dataproc submission via Composer | [`06-orchestration-architecture.md`](06-orchestration-architecture.md) | Yes |
| #9 Gap between documented security policy and actual configuration | High | Deliberate, reviewed IAM/Secret Manager/KMS design — not a 1:1 port of current state | [`07-security-architecture-overview.md`](07-security-architecture-overview.md) | Yes — full closure verified in [`10-security/`](../10-security/README.md) |
| #10 Scarce/aging on-prem Hadoop admin talent | Medium (strategic) | Reduced operational burden via managed services | Entire target architecture | Yes (indirectly, over time) |

_(Rows must mirror
[`03-current-environment/09-pain-points-and-bottlenecks.md`](../03-current-environment/09-pain-points-and-bottlenecks.md)
exactly — if that document is updated with additional findings, this
matrix must be updated in the same change.)_

## Sign-off

| Pain Point # | Resolution Accepted By | Date |
|---|---|---|
| #7 (partial resolution — requires execution discipline) | Migration Program Lead + Platform Engineering Lead | _(date)_ |

Only pain points marked "Partial" or "No" require explicit sign-off here —
fully resolved items are self-evident from the matrix above and don't need
a separate approval record.

## Common Mistakes

- Marking a pain point "Resolved: Yes" because the target architecture
  *could* resolve it in principle, without a specific document reference
  showing the actual design decision — every "Yes" must cite where.
- Letting this matrix go stale after new pain points are discovered later
  in the program (e.g., during
  [`12-cluster-design/`](../12-cluster-design/README.md) implementation) —
  update it whenever
  [`03-current-environment/09-pain-points-and-bottlenecks.md`](../03-current-environment/09-pain-points-and-bottlenecks.md)
  changes.
