# Hive Migration Execution Runbook

**Purpose:** A single sequential checklist tying together every document
in this folder, applied per database/table group.
**Owner:** Data Engineering (executor).

---

## Runbook — Database/Table Group: `_______________`

### 1. Pre-migration

- [ ] Per-table target decisions confirmed (BigQuery / Dataproc-Hive) per
      [`04-target-architecture/05-data-warehouse-architecture.md`](../04-target-architecture/05-data-warehouse-architecture.md)
- [ ] Table type (external/managed) confirmed per
      [`02-external-vs-managed-table-migration.md`](02-external-vs-managed-table-migration.md)
- [ ] Dependency order established for views and UDFs per
      [`02-dependency-analysis/methodology/02-hive-dependencies.md`](../02-dependency-analysis/methodology/02-hive-dependencies.md)
- [ ] Underlying data migration complete and validated per
      [`06-data-migration/`](../06-data-migration/README.md)

### 2. Metastore / table DDL (Dataproc-Hive targets only)

- [ ] Dataproc Metastore provisioned per
      [`01-metastore-migration-strategy.md`](01-metastore-migration-strategy.md)
- [ ] DDL exported, translated, and executed against target

### 3. Native table creation (BigQuery targets only)

- [ ] BigQuery dataset/table created via Terraform per
      [`13-infrastructure/`](../13-infrastructure/README.md)
- [ ] Partitioning/clustering applied per
      [`06-data-migration/05-partition-strategy.md`](../06-data-migration/05-partition-strategy.md)

### 4. Partition registration

- [ ] Partitions registered/validated per
      [`03-partition-migration.md`](03-partition-migration.md)
- [ ] Partition count reconciled against source

### 5. Statistics

- [ ] Statistics computed per
      [`04-statistics-migration.md`](04-statistics-migration.md)
      (Dataproc-Hive targets)

### 6. UDFs (if any referenced by this table group)

- [ ] Every UDF's behavior documented from the source implementation
- [ ] UDF reimplemented and side-by-side validated per
      [`06-udf-migration.md`](06-udf-migration.md)

### 7. Views (in dependency order)

- [ ] Every view migrated in correct dependency order per
      [`05-view-migration.md`](05-view-migration.md)
- [ ] Output equivalence validated per view

### 8. Sign-off

- [ ] Reconciliation report (schema, row counts, sample data) reviewed by
      Data Engineering
- [ ] Business Owner sign-off obtained for Tier 1 tables/views/UDFs
- [ ] Recorded complete in
      [`14-job-migration/`](../14-job-migration/README.md) tracker

**Executed by:** ________________ **Date:** ________________
**Reviewed by:** ________________ **Date:** ________________

## Common Mistakes

- Executing steps out of order (e.g., migrating views before their base
  tables' partitions are registered) — follow the sequence above exactly,
  since later steps assume earlier steps are genuinely complete, not just
  started.
- Treating this runbook as a formality for "simple" databases — the
  discipline matters most precisely when a migration starts to feel
  routine and shortcuts become tempting.
