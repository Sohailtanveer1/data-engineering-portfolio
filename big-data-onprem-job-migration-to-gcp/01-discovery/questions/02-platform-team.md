# Discovery Questions — Platform Team (On-Prem Hadoop Admins)

**Purpose:** The platform team holds the ground-truth operational knowledge
of the cluster that no dashboard fully captures — undocumented quirks,
manual interventions, and the "we always do X before Y because last time we
didn't, it broke" knowledge that must be captured before it walks out the
door.
**Owner:** Migration Program Lead, conducted with Platform Engineering lead.
**Audience:** Hadoop cluster administrators, YARN/HDFS operators, Hive
Metastore DBAs.
**Inputs:** Cluster access, existing runbooks (if any).
**Outputs:** Feeds [`03-current-environment/`](../../03-current-environment/README.md)
directly; feeds [`11-storage-inventory.md`](../inventories/11-storage-inventory.md)
and [`10-scheduler-inventory.md`](../inventories/10-scheduler-inventory.md).

---

## Questions

| # | Question | Why we ask it |
|---|---|---|
| 1 | Walk me through what you do during a typical incident on this cluster — what breaks most often? | Recurring incidents point directly at fragile components that need extra validation post-migration, and at operational pain points the migration should actually fix, not just relocate. |
| 2 | Are there manual steps performed regularly that aren't in any runbook (e.g., "I clear this directory every Sunday")? | Undocumented manual maintenance is exactly the kind of thing that silently breaks after cutover when the person who did it moves on or isn't asked. |
| 3 | What is the current HDFS capacity, utilization, and growth rate? | Directly sizes the storage migration effort and target GCS bucket capacity planning in [`05-storage-migration/`](../../05-storage-migration/README.md). |
| 4 | What Hadoop/Spark/Hive/YARN versions are actually running (not what's documented)? | Version drift between documentation and reality is extremely common; this is the single most load-bearing fact for [`07-spark-migration/`](../../07-spark-migration/README.md) API-compatibility planning. |
| 5 | Are there custom patches, forks, or vendor-specific extensions applied to the distribution? | Custom patches may have no GCP equivalent and need explicit redesign, not just reinstallation. |
| 6 | How is capacity currently allocated across teams/queues, and where are the contention points? | Informs [`12-cluster-design/`](../../12-cluster-design/README.md) sizing and whether ephemeral per-job clusters solve a real contention problem. |
| 7 | What's the current backup/DR process for HDFS and the Hive Metastore, and has a restore ever actually been tested? | An untested backup is not a backup. This directly feeds [`05-disaster-recovery-rpo-rto.md`](../inventories/05-disaster-recovery-rpo-rto.md). |
| 8 | Which nodes, racks, or components are known to be flaky or end-of-life? | Hardware nearing end-of-life increases urgency for the jobs running on it and may justify accelerating specific waves. |
| 9 | How are OS-level and Hadoop-stack security patches currently applied, and how far behind are we? | Feeds the security assessment and may reveal urgency independent of the migration itself. |
| 10 | Is there a change freeze process today, and has it ever been violated under business pressure? | Signals how much organizational discipline we can expect the freeze windows in the charter to actually receive. |
| 11 | What tooling do you use today for monitoring cluster health, and what do you wish you had? | Directly informs [`18-monitoring/`](../../18-monitoring/README.md) design — build what's actually missing, not a generic dashboard. |
| 12 | Which jobs or workflows do you personally consider fragile or "held together with tape"? | Platform admins often know exactly which jobs are landmines well before the job owners admit it. |

## Validation of answers

Cross-reference version and capacity claims against actual cluster
configuration files and `hdfs dfsadmin -report` / YARN REST API output,
captured directly in [`03-current-environment/`](../../03-current-environment/README.md).
