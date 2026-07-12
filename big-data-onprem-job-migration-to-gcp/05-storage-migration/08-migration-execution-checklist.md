# Storage Migration Execution Checklist (Per Data Domain)

**Purpose:** A single reusable checklist, copied and filled in per data
domain, ensuring every storage migration follows the same rigor regardless
of who executes it or how routine it starts to feel after the first few
domains.
**Owner:** Platform Engineering (executor for each domain).
**When to use:** Once per data domain, from
[`01-discovery/inventories/11-storage-inventory.md`](../01-discovery/inventories/11-storage-inventory.md),
before that domain's migration wave.

---

## Checklist — Data Domain: `_______________`

### Pre-migration

- [ ] Target GCS bucket exists (created via Terraform,
      [`13-infrastructure/`](../13-infrastructure/README.md))
- [ ] Volume and file count confirmed against
      [`01-discovery/inventories/11-storage-inventory.md`](../01-discovery/inventories/11-storage-inventory.md)
- [ ] Transfer tool selected per
      [`01-migration-strategy-overview.md`](01-migration-strategy-overview.md)
      decision framework, with rationale recorded
- [ ] Transfer window scheduled against
      [`01-discovery/inventories/03-peak-hours-and-downtime-windows.md`](../01-discovery/inventories/03-peak-hours-and-downtime-windows.md)
      off-peak guidance
- [ ] IAM/permissions mapping completed and reviewed per
      [`06-permissions-and-metadata-migration.md`](06-permissions-and-metadata-migration.md)
- [ ] Security sign-off obtained if the mapping widens any access
- [ ] Operations/on-call team notified of transfer window (Tier 1 domains)

### Migration execution

- [ ] Dry run executed and reviewed
- [ ] Bulk transfer executed
- [ ] Transfer completion confirmed (no errors in tool-specific logs)
- [ ] Execution logged in [`logs/`](../logs/README.md)

### Validation

- [ ] Level 1 (file count/size) validation passed
- [ ] Level 2 (checksum) validation passed — 100% coverage for Tier 1, full
      or statistically sound sample otherwise
- [ ] Level 3 (content spot-check) validation passed
- [ ] Level 4 (row/record count reconciliation) validation passed, for
      structured data
- [ ] Validation report reviewed and signed off by Data Engineering
      (domain owner)
- [ ] Validation report reviewed and signed off by Platform Engineering

### Incremental sync (if domain not yet fully cut over)

- [ ] Incremental sync mechanism configured per
      [`04-incremental-sync-strategy.md`](04-incremental-sync-strategy.md)
- [ ] Sync lag monitoring/alerting configured per
      [`18-monitoring/`](../18-monitoring/README.md)

### Sign-off

- [ ] Recorded as complete in
      [`14-job-migration/`](../14-job-migration/README.md) tracker
- [ ] Rollback procedure confirmed understood by the executing engineer
      (per [`07-rollback-procedure.md`](07-rollback-procedure.md)) —
      no action needed unless a trigger condition occurs

**Executed by:** ________________ **Date:** ________________
**Reviewed by:** ________________ **Date:** ________________

## Common Mistakes

- Skipping checklist items for "simple" domains because the process feels
  redundant after the first few executions — the checklist exists
  precisely to prevent complacency-driven shortcuts as the team gains
  (over-)confidence.
- Filling in the checklist retroactively after the fact instead of using
  it as a live execution guide — this defeats its purpose as a pre-flight
  safeguard, not just a compliance record.
