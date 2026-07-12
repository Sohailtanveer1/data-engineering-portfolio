# Rollback Plan (Cutover-Specific)

**Purpose:** The specific, rehearsed rollback execution plan for a
cutover event — building on the general procedures in
[`14-job-migration/06-rollback-procedures.md`](../14-job-migration/06-rollback-procedures.md)
with the exact steps for this specific job/wave.
**Owner:** Migration Program Lead (decision authority), Platform
Engineering (execution).

---

## Rollback trigger criteria (defined in advance)

Every cutover event has explicit, pre-agreed rollback triggers, not a
judgment call made under pressure in the moment:

| Trigger | Example |
|---|---|
| Post-cutover validation fails | Reconciliation check per [`07-post-cutover-validation.md`](07-post-cutover-validation.md) shows a discrepancy |
| Job fails to complete within [X]x its expected duration | Signals a performance or configuration issue |
| A P1/P2 incident is directly attributed to the cutover | Any severity-1/2 issue traced to the migrated job |
| Business Owner reports the output is unusable | Even if technical validation passed, a business-side red flag is a valid trigger |

## Rollback execution steps (reverse of deployment sequence)

1. **Decision made** by Command Center Lead, per the trigger criteria.
2. **Re-enable the on-prem scheduler entry** (per
   [`05-storage-migration/07-rollback-procedure.md`](../05-storage-migration/07-rollback-procedure.md)
   — only possible if not yet decommissioned).
3. **Pause the Composer DAG** for the affected job.
4. **Redirect downstream consumers back** to the on-prem output location.
5. **Communicate the rollback** per
   [`03-communication-plan.md`](03-communication-plan.md), transparently
   — a clean rollback is the safety mechanism working, not a failure to
   hide.
6. **Verify on-prem is functioning correctly** post-rollback (the on-prem
   job hasn't run in a while if it was paused during parallel-run — confirm
   it resumes cleanly).
7. **Root-cause the triggering issue** before attempting cutover again.

## Rollback time target

Every cutover event's go-live plan (per
[`01-go-live-plan.md`](01-go-live-plan.md)) specifies a target rollback
execution time (e.g., "rollback executable within 30 minutes of
decision") — validated during `stage` rehearsal, not just assumed.

## Rollback rehearsal

The rollback path is rehearsed in `stage` with the same rigor as the
forward deployment sequence — a rollback plan that's never been executed,
even in rehearsal, is a plan of unknown reliability exactly when
reliability matters most.

## Common Mistakes

- Defining rollback triggers vaguely ("if something looks wrong") instead
  of specific, objective criteria decided in advance — vague criteria
  invite hesitation and delay exactly when a fast decision matters.
- Never actually rehearsing the rollback, only the forward path — this is
  the single most common gap in cutover planning.

## Production Notes

For every Tier 1 cutover, the rollback rehearsal in `stage` must be timed
and the actual measured rollback duration compared against the RTO
requirement from
[`01-discovery/inventories/05-disaster-recovery-rpo-rto.md`](../01-discovery/inventories/05-disaster-recovery-rpo-rto.md)
— if rehearsed rollback takes longer than the RTO allows, this is a gap
that must be closed before that job is approved for cutover.
