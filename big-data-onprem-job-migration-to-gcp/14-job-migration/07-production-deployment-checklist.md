# Production Deployment Checklist (Per Job)

**Purpose:** The final go/no-go checklist before a job's actual production
cutover — the last gate before
[`21-cutover/`](../21-cutover/README.md) execution.
**Owner:** Migration Program Lead (approver), Platform Engineering
(executor).

---

## Checklist — Job: `_______________`

### Prerequisite phases

- [ ] Storage and data migration validated per
      [`06-data-migration/07-data-reconciliation-framework.md`](../06-data-migration/07-data-reconciliation-framework.md)
- [ ] Hive migration validated (if applicable) per
      [`08-hive-migration/07-execution-runbook.md`](../08-hive-migration/07-execution-runbook.md)
- [ ] Spark job code complete, tested (unit + integration + idempotency)
      per [`07-spark-migration/`](../07-spark-migration/README.md)
- [ ] Composer DAG built, tested per
      [`09-composer-migration/`](../09-composer-migration/README.md)
- [ ] Security review approved per
      [`10-security/08-execution-and-review-checklist.md`](../10-security/08-execution-and-review-checklist.md)
- [ ] Cluster configuration validated under load per
      [`17-performance/`](../17-performance/README.md)

### Parallel-run

- [ ] Minimum parallel-run duration for this job's tier met, per
      [`04-parallel-run-strategy.md`](04-parallel-run-strategy.md)
- [ ] Zero unresolved reconciliation failures in the qualifying window
- [ ] Peak/edge-case period covered (Tier 1)

### Sign-off

- [ ] UAT sign-off obtained (Tier 1/2) per
      [`20-uat/`](../20-uat/README.md)
- [ ] Business Owner sign-off obtained (Tier 1)

### Operational readiness

- [ ] Monitoring dashboards and alerts live per
      [`18-monitoring/`](../18-monitoring/README.md)
- [ ] Runbook for this job's common failure modes documented in
      [`runbooks/`](../runbooks/README.md)
- [ ] On-call team briefed on this job's cutover and knows the rollback
      procedure

### Scheduling

- [ ] Cutover date confirmed outside any charter freeze window per
      [`00-project-overview/02-migration-charter.md`](../00-project-overview/02-migration-charter.md)
- [ ] Cutover sequenced correctly within
      [`21-cutover/`](../21-cutover/README.md) deployment sequence if part
      of a multi-job wave cutover

### Final go/no-go

- [ ] Migration Program Lead approval
- [ ] Business Owner approval (Tier 1)
- [ ] No open, unresolved blockers in
      [`03-migration-tracker.md`](03-migration-tracker.md)

**Approved by:** ________________ **Date:** ________________
**Cutover scheduled for:** ________________

## Common Mistakes

- Proceeding with a partial checklist under schedule pressure, treating
  unchecked items as "we'll catch up during hypercare" — every item here
  exists because skipping it has caused a real problem in comparable
  migrations.
- Approving go/no-go without the Business Owner for a Tier 1 job, even
  when engineering is confident — the sign-off exists specifically to
  catch what engineering alone might miss.
