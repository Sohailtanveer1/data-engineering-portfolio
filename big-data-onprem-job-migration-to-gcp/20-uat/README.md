# 20 — User Acceptance Testing

## Purpose

The final human checkpoint before production cutover — where the actual
Business Owner, not just engineering, confirms a migrated job/dataset is
ready for production reliance. Every prior validation
([`15-testing/`](../15-testing/README.md),
[`16-data-validation/`](../16-data-validation/README.md)) is engineering-
led; UAT is business-led, and exists specifically to catch what
engineering's own validation cannot — whether the migrated output is
actually usable and correct from the business's perspective.

## Owner

**Business Owner** (per job/domain, per the RACI in
[`00-project-overview/03-raci-matrix.md`](../00-project-overview/03-raci-matrix.md)),
facilitated by QA and the Migration Program Lead.

## Inputs

- Passed [`15-testing/`](../15-testing/README.md) and
  [`16-data-validation/`](../16-data-validation/README.md) results.
- Completed parallel-run per
  [`14-job-migration/04-parallel-run-strategy.md`](../14-job-migration/04-parallel-run-strategy.md).

## Outputs

- Signed business acceptance for every Tier 1/2 job before cutover.
- A logged, resolved issue list for anything found during UAT.

## Prerequisites

[`14-job-migration/04-parallel-run-strategy.md`](../14-job-migration/04-parallel-run-strategy.md)
minimum duration met with zero unresolved reconciliation failures.

## Deliverables

1. Acceptance criteria (per job/domain, agreed in advance).
2. UAT execution checklist.
3. Business sign-off process.
4. Issue tracking and resolution process.

## Risks

UAT surfacing a fundamental issue late, after significant migration
investment, is a real risk this phase exists to catch **before** cutover
rather than after — the cost of finding an issue here is much lower than
finding it in production.

## Rollback

N/A — UAT itself doesn't modify anything; a failed UAT simply blocks
cutover until resolved, per
[`14-job-migration/07-production-deployment-checklist.md`](../14-job-migration/07-production-deployment-checklist.md).

## Validation

UAT is itself a validation gate — "validating" UAT means confirming every
Tier 1/2 job has genuine, informed Business Owner sign-off, not a rubber
stamp.

## Best Practices

Define acceptance criteria **before** UAT begins, agreed with the
Business Owner in advance — evaluating against criteria decided
after the fact invites scope creep or, conversely, insufficient scrutiny.

## Lessons Learned

UAT conducted as a formality (a quick demo, immediate sign-off) rather
than genuine hands-on business testing misses issues that only surface
when the actual end user interacts with the migrated output in their real
workflow.

## Common Mistakes

- Scheduling UAT so tightly against the cutover date that there's no time
  to resolve an issue found during UAT without delaying cutover.
- Having engineering demo the output to the Business Owner instead of the
  Business Owner directly interacting with it themselves.

## Production Notes

For Tier 1 domains, budget UAT time generously in the wave plan — a
rushed UAT defeats its purpose as the final, business-perspective safety
check.

---

## Folder structure

```
20-uat/
├── README.md                                   This file
├── 01-acceptance-criteria.md                    Per-job/domain, agreed in advance
├── 02-uat-execution-checklist.md                Step-by-step UAT process
├── 03-business-signoff-process.md               Formal sign-off mechanism
└── 04-issue-tracking-and-resolution.md          Logging and resolving UAT findings
```
