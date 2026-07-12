# Rollback Procedures (Job & Wave Level)

**Purpose:** Consolidate the rollback guidance scattered across earlier
phase folders into a single, job-migration-level reference, plus define
wave-level rollback coordination.
**Owner:** Migration Program Lead (decision authority), Platform
Engineering (execution).

---

## Job-level rollback (pre-cutover)

Before a job's actual production cutover, rollback is inherently low-risk:
the on-prem job remains system of record throughout
[`04-parallel-run-strategy.md`](04-parallel-run-strategy.md) — "rolling
back" simply means pausing/fixing the GCP-side work without any production
impact, per
[`05-storage-migration/07-rollback-procedure.md`](../05-storage-migration/07-rollback-procedure.md).

## Job-level rollback (post-cutover)

Once a job has cut over (GCP is now system of record), rollback means
reverting to on-prem as system of record temporarily:

1. **Trigger**: a P1/P2 issue traced to the migrated job, not resolvable
   quickly enough to meet SLA via forward-fix.
2. **Decision**: Migration Program Lead has standing authority to decide
   (per the RACI cutover-decision escalation), consulting the on-call
   Platform Engineer and Business Owner if time allows.
3. **Execution**:
   - Re-enable the on-prem job/scheduler entry (only possible if not yet
     decommissioned — see the decommissioning gate in
     [`05-storage-migration/07-rollback-procedure.md`](../05-storage-migration/07-rollback-procedure.md)).
   - Pause the Composer DAG for the GCP job.
   - Redirect any downstream consumers back to the on-prem output location
     if they had already been repointed.
4. **Post-rollback**: root-cause the issue, fix, re-validate via a fresh
   (shortened, targeted) parallel-run focused on the specific failure
   scenario, then re-attempt cutover.

## Wave-level rollback

If multiple jobs in a wave are cut over together and a systemic issue
affects the wave broadly (e.g., a shared library bug discovered post-
cutover, per the blast-radius risk in
[`07-spark-migration/README.md`](../07-spark-migration/README.md)):

1. Assess whether the issue is isolated to one job or affects the shared
   pattern broadly.
2. If broad, roll back every affected job in the wave using the job-level
   procedure above, prioritizing Tier 1 jobs first.
3. Halt further wave progression until the systemic issue is resolved and
   validated.

## What must remain available for rollback to work

- On-prem job/scheduler entries not yet decommissioned (per the
  decommissioning gate).
- On-prem source data intact (never modified by the migration itself, per
  constraint C7).
- A clear, tested procedure for redirecting downstream consumers back to
  the on-prem output — this must be validated during
  [`15-testing/`](../15-testing/README.md), not assumed to work the first
  time it's actually needed.

## Rollback decision log

Every rollback (attempted or executed) is logged in
[`logs/`](../logs/README.md) with root cause, decision rationale, and
resolution — feeding lessons learned into
[`documentation/`](../documentation/README.md) and informing whether the
wave plan or execution process itself needs adjustment.

## Common Mistakes

- Decommissioning an on-prem job prematurely (before the hypercare gate),
  removing the rollback safety net before it's genuinely no longer needed.
- Treating a rollback as a failure to be avoided reporting — a rollback
  executed cleanly and quickly is the safety mechanism working as
  designed, not a program failure; the goal is safe, fast rollback when
  needed, not zero rollbacks at any cost.

## Production Notes

Rehearse the rollback procedure for at least one Tier 1 job explicitly
during [`15-testing/`](../15-testing/README.md) chaos/recovery testing —
before relying on it for the first time during an actual incident.
