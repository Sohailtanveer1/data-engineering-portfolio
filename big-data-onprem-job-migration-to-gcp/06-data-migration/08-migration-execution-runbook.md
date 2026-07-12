# Data Migration Execution Runbook (Per Table)

**Purpose:** A single, sequential, end-to-end runbook per table, tying
together every document in this folder into one executable procedure —
the practical entry point for an engineer executing a table's data
migration, rather than needing to separately consult seven different
strategy documents in the right order.
**Owner:** Data Engineering (executor).
**When to use:** Once per table, after
[`05-storage-migration/`](../05-storage-migration/README.md) has completed
for the table's data domain and the table's BigQuery/Dataproc-Hive target
decision is finalized per
[`04-target-architecture/05-data-warehouse-architecture.md`](../04-target-architecture/05-data-warehouse-architecture.md).

---

## Runbook — Table: `_______________`

### 1. Pre-migration setup

- [ ] Target decision confirmed (BigQuery / Dataproc-Hive) per
      [`04-target-architecture/05-data-warehouse-architecture.md`](../04-target-architecture/05-data-warehouse-architecture.md)
- [ ] Target table/dataset created via Terraform
      ([`13-infrastructure/`](../13-infrastructure/README.md)), with
      correct partition scheme per
      [`05-partition-strategy.md`](05-partition-strategy.md)
- [ ] Format/compression standard confirmed per
      [`06-format-and-compression-strategy.md`](06-format-and-compression-strategy.md)
- [ ] Retention window confirmed per
      [`01-discovery/inventories/04-data-retention-and-compliance.md`](../01-discovery/inventories/04-data-retention-and-compliance.md)
- [ ] CDC requirement evaluated per
      [`03-cdc-strategy.md`](03-cdc-strategy.md) (Yes/No, and if yes,
      pipeline built and tested)

### 2. Pre-migration snapshot

- [ ] Source snapshot taken per
      [`04-snapshot-strategy.md`](04-snapshot-strategy.md)
- [ ] Snapshot reference recorded for reconciliation use

### 3. Historical backfill

- [ ] Batching plan defined per
      [`01-historical-data-migration-plan.md`](01-historical-data-migration-plan.md)
- [ ] Each batch loaded (idempotent write) and individually reconciled per
      [`07-data-reconciliation-framework.md`](07-data-reconciliation-framework.md)
      before proceeding to the next batch
- [ ] Full historical range confirmed complete and reconciled

### 4. Incremental load setup

- [ ] Watermark mechanism designed and implemented per
      [`02-incremental-load-strategy.md`](02-incremental-load-strategy.md)
      (if CDC was not selected)
- [ ] Watermark store initialized with the correct starting value (end of
      historical backfill range)
- [ ] First incremental run executed and reconciled

### 5. Ongoing parallel-run validation

- [ ] Incremental load running on schedule, monitored per
      [`18-monitoring/`](../18-monitoring/README.md)
- [ ] Periodic reconciliation snapshots taken and checked per
      [`04-snapshot-strategy.md`](04-snapshot-strategy.md) cadence
- [ ] No unresolved reconciliation discrepancies outstanding

### 6. Sign-off

- [ ] Reconciliation report reviewed by Data Engineering
- [ ] Reconciliation report reviewed by Business Owner's technical contact
      (Tier 1 tables only)
- [ ] Table marked complete in
      [`14-job-migration/`](../14-job-migration/README.md) tracker
- [ ] Ready for the owning job's cutover per
      [`21-cutover/`](../21-cutover/README.md)

**Executed by:** ________________ **Date:** ________________
**Reviewed by:** ________________ **Date:** ________________

## Common Mistakes

- Proceeding to incremental load setup before historical backfill is fully
  reconciled — this makes it impossible to distinguish a historical-load
  discrepancy from an incremental-load discrepancy if problems surface
  later.
- Treating this runbook as optional for "simple" tables — the checklist
  discipline is what prevents the most common, avoidable data migration
  mistakes documented throughout this folder.
