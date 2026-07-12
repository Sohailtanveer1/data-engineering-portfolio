# 21 — Cutover

## Purpose

The actual go-live execution — the moment a job (or wave of jobs)
switches from on-prem to GCP as system of record. Every prior phase exists
to make this moment low-risk and well-rehearsed; this folder defines
exactly how it's executed, communicated, and — if necessary — reversed.

## Owner

**Migration Program Lead** (command center lead), executed by Platform/
Data Engineering, with Business Owner and Operations engaged per the
communication plan.

## Inputs

- UAT sign-off from [`20-uat/`](../20-uat/README.md).
- Completed production deployment checklist from
  [`14-job-migration/07-production-deployment-checklist.md`](../14-job-migration/07-production-deployment-checklist.md).
- Confirmed date outside any freeze window per
  [`00-project-overview/02-migration-charter.md`](../00-project-overview/02-migration-charter.md).

## Outputs

- Jobs successfully running on GCP as system of record.
- A documented cutover execution record for
  [`documentation/`](../documentation/README.md) and
  [`logs/`](../logs/README.md).

## Prerequisites

Every gate in
[`14-job-migration/07-production-deployment-checklist.md`](../14-job-migration/07-production-deployment-checklist.md)
passed.

## Deliverables

1. Go-live plan.
2. Command center operations model.
3. Communication plan.
4. Freeze plan (pre/post cutover change freeze).
5. Deployment sequence.
6. Rollback plan.
7. Post-cutover validation.

## Risks

Cutover is the single highest-risk moment in the entire program — every
risk mitigated throughout this repository converges here. This folder's
rigor is proportional to that concentration of risk.

## Rollback

The full rollback plan is detailed in
[`06-rollback-plan.md`](06-rollback-plan.md), building on
[`14-job-migration/06-rollback-procedures.md`](../14-job-migration/06-rollback-procedures.md).

## Validation

Post-cutover validation (per
[`07-post-cutover-validation.md`](07-post-cutover-validation.md)) confirms
the cutover succeeded — cutover isn't "done" the moment the switch is
flipped, only once validated.

## Best Practices

Rehearse the cutover sequence in `stage` before the real event — a
cutover with no rehearsal is a cutover where the command center is
learning the process live, under real pressure.

## Lessons Learned

Cutovers that go smoothly are usually the ones with the most boring,
thorough rehearsal beforehand — the goal is for the actual cutover to feel
anticlimactic because everything unexpected was already found in
rehearsal.

## Common Mistakes

- Scheduling cutover without a rehearsed rollback path tested end-to-end.
- Under-communicating cutover timing to stakeholders, causing confusion
  or unplanned interference from other teams during the window.

## Production Notes

Every Tier 1 cutover requires a full command center activation per
[`02-command-center-operations.md`](02-command-center-operations.md) —
never executed as a routine, unstaffed deployment.

---

## Folder structure

```
21-cutover/
├── README.md                              This file
├── 01-go-live-plan.md                      Overall go-live plan and timeline
├── 02-command-center-operations.md         Roles, staffing, decision authority during cutover
├── 03-communication-plan.md                Who is told what, when
├── 04-freeze-plan.md                       Pre/post cutover change freeze
├── 05-deployment-sequence.md               Exact technical execution order
├── 06-rollback-plan.md                     Full rollback execution plan
└── 07-post-cutover-validation.md            Confirming success, not just execution
```
