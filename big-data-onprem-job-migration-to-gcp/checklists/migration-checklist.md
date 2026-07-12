# Master Migration Checklist (Per Job)

**Purpose:** The single-page, end-to-end view of every gate a job passes
through — a quick reference index into the detailed checklists living in
each phase. For actual execution, use the detailed checklist linked at
each step, not this summary alone.
**Owner:** Migration Program Lead.

---

## Checklist — Job: `_______________`

- [ ] **Discovery**: Job catalogued in [`01-discovery/inventories/06-job-inventory.md`](../01-discovery/inventories/06-job-inventory.md), tiered in [`01-discovery/inventories/02-business-critical-jobs.md`](../01-discovery/inventories/02-business-critical-jobs.md)
- [ ] **Dependency Analysis**: Dependency card complete per [`02-dependency-analysis/templates/02-job-dependency-card-template.md`](../02-dependency-analysis/templates/02-job-dependency-card-template.md)
- [ ] **Storage Migration**: Data domain migrated per [`05-storage-migration/08-migration-execution-checklist.md`](../05-storage-migration/08-migration-execution-checklist.md)
- [ ] **Data Migration**: Table(s) migrated per [`06-data-migration/08-migration-execution-runbook.md`](../06-data-migration/08-migration-execution-runbook.md)
- [ ] **Hive Migration** (if applicable): Per [`08-hive-migration/07-execution-runbook.md`](../08-hive-migration/07-execution-runbook.md)
- [ ] **Spark Migration**: Job code complete, tested, idempotent per [`07-spark-migration/README.md`](../07-spark-migration/README.md)
- [ ] **Composer Migration**: DAG built and tested per [`09-composer-migration/README.md`](../09-composer-migration/README.md)
- [ ] **Security Review**: Per [`10-security/08-execution-and-review-checklist.md`](../10-security/08-execution-and-review-checklist.md)
- [ ] **Testing**: All applicable test types per [`15-testing/01-test-strategy-overview.md`](../15-testing/01-test-strategy-overview.md) tier requirements
- [ ] **Data Validation**: Reconciliation passing per [`16-data-validation/06-reconciliation-reporting.md`](../16-data-validation/06-reconciliation-reporting.md)
- [ ] **Performance**: SLA met under representative load per [`17-performance/`](../17-performance/README.md)
- [ ] **Monitoring**: Dashboards and alerts live per [`18-monitoring/`](../18-monitoring/README.md)
- [ ] **Parallel-Run**: Minimum duration met per [`14-job-migration/04-parallel-run-strategy.md`](../14-job-migration/04-parallel-run-strategy.md)
- [ ] **UAT**: Business sign-off obtained per [`20-uat/03-business-signoff-process.md`](../20-uat/03-business-signoff-process.md)
- [ ] **Production Deployment**: Full checklist passed per [`14-job-migration/07-production-deployment-checklist.md`](../14-job-migration/07-production-deployment-checklist.md)
- [ ] **Cutover**: Executed per [`21-cutover/05-deployment-sequence.md`](../21-cutover/05-deployment-sequence.md), validated per [`21-cutover/07-post-cutover-validation.md`](../21-cutover/07-post-cutover-validation.md)
- [ ] **Hypercare**: Exit criteria met per [`22-hypercare/01-elevated-monitoring-plan.md`](../22-hypercare/01-elevated-monitoring-plan.md)
- [ ] **Handover**: Complete per [`22-hypercare/03-knowledge-transfer-and-handover.md`](../22-hypercare/03-knowledge-transfer-and-handover.md)

**Tracked live in:** [`14-job-migration/03-migration-tracker.md`](../14-job-migration/03-migration-tracker.md)
