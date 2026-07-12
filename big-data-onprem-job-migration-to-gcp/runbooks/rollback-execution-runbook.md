# Runbook: Rollback Execution

## Trigger

A rollback decision has been made per
[`14-job-migration/06-rollback-procedures.md`](../14-job-migration/06-rollback-procedures.md)
or
[`21-cutover/06-rollback-plan.md`](../21-cutover/06-rollback-plan.md), and
needs to be executed.

## Pre-execution confirmation

- [ ] Rollback decision authority confirmed (Migration Program Lead, per
      the RACI).
- [ ] On-prem source confirmed not yet decommissioned (per
      [`05-storage-migration/07-rollback-procedure.md`](../05-storage-migration/07-rollback-procedure.md)
      decommissioning gate) — if it has been decommissioned, this is a
      different, more involved recovery scenario requiring escalation to
      the Migration Program Lead before any further action.

## Execution steps

1. **Re-enable the on-prem scheduler entry** for the affected job.
2. **Pause the Composer DAG**:
   ```bash
   gcloud composer environments run <composer-env> \
     --location <region> \
     dags pause -- <dag_id>
   ```
3. **Redirect downstream consumers** back to the on-prem output location
   — per the job's specific downstream consumer list in its dependency
   card.
4. **Verify on-prem resumes correctly** — confirm the next scheduled
   on-prem run completes successfully.
5. **Communicate** per
   [`21-cutover/03-communication-plan.md`](../21-cutover/03-communication-plan.md).

## Post-rollback

1. Root-cause the triggering issue (see
   [`job-failure-diagnosis-runbook.md`](job-failure-diagnosis-runbook.md)
   or
   [`validation-failure-investigation-runbook.md`](validation-failure-investigation-runbook.md)
   as applicable).
2. Fix and re-validate before attempting cutover again — do not re-attempt
   cutover without addressing root cause.
3. Log the rollback in
   [`logs/`](../logs/README.md) and
   [`documentation/issue-tracker.md`](../documentation/issue-tracker.md).

## Escalation

A rollback that cannot be executed cleanly (e.g., the on-prem source has
already been decommissioned, or downstream redirection isn't working)
escalates immediately to the Migration Program Lead — this is a
higher-severity situation than a standard rollback and may require a
broader incident response.
