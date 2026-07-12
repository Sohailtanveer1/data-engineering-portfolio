# 22 — Hypercare

## Purpose

The defined stabilization period immediately following cutover, with
elevated monitoring and dedicated support — bridging the gap between "just
cut over" and "fully absorbed into standard operations." This is also
where the migration program formally closes out: knowledge transfer,
post-implementation review, and lessons learned feeding back into
[`documentation/`](../documentation/README.md) for the next wave or the
next migration this company undertakes.

## Owner

**Migration Program Lead**, with Operations taking increasing ownership
as hypercare progresses toward standard operations handover.

## Inputs

- Successfully cut-over job(s) from
  [`21-cutover/07-post-cutover-validation.md`](../21-cutover/07-post-cutover-validation.md).

## Outputs

- A stable, fully-operational job under standard (not elevated) monitoring.
- Complete knowledge transfer to standing Operations.
- A post-implementation review and lessons-learned record.

## Prerequisites

Cutover complete per
[`21-cutover/07-post-cutover-validation.md`](../21-cutover/07-post-cutover-validation.md).

## Deliverables

1. Elevated monitoring plan (duration, what's elevated, exit criteria).
2. Issue management process during hypercare.
3. Knowledge transfer and handover to standing Operations.
4. Support runbook index.
5. Post-implementation review.
6. Lessons learned and closeout.

## Risks

Ending hypercare too early, before the platform has genuinely stabilized,
risks issues surfacing after the safety net of elevated attention and
readily-available rollback has been removed.

## Rollback

Rollback remains available throughout hypercare per
[`21-cutover/06-rollback-plan.md`](../21-cutover/06-rollback-plan.md) —
this is part of why hypercare exists as a distinct period with its own
elevated readiness.

## Validation

Hypercare exit criteria (per
[`01-elevated-monitoring-plan.md`](01-elevated-monitoring-plan.md)) must
be explicitly met, not just a fixed calendar duration elapsed — a job with
ongoing issues doesn't exit hypercare just because 30 days have passed.

## Best Practices

Use hypercare actively — daily review of monitoring, validation, and
issue status — not passively waiting to see if something goes wrong.

## Lessons Learned

The value of hypercare is proportional to how actively it's used;
treating it as a passive waiting period rather than an active
stabilization effort wastes its primary benefit.

## Common Mistakes

- Ending hypercare on a fixed calendar date regardless of actual
  stability.
- Skipping the post-implementation review because the team is eager to
  move to the next wave — this loses the improvement feedback loop for
  every subsequent wave.

## Production Notes

For Tier 1 jobs, hypercare should specifically extend through at least
one instance of the job's highest-complexity operational scenario (a
month-end close, a peak trading event) before being considered eligible
to close.

---

## Folder structure

```
22-hypercare/
├── README.md                                    This file
├── 01-elevated-monitoring-plan.md                Duration, scope, exit criteria
├── 02-issue-management-process.md                How issues are triaged and resolved during hypercare
├── 03-knowledge-transfer-and-handover.md         Migration team → standing Operations
├── 04-support-runbook-index.md                   Support model and runbook navigation
├── 05-post-implementation-review.md              Formal review process
└── 06-lessons-learned-and-closeout.md            Capturing and feeding back learnings
```
