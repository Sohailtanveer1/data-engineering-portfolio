# 14 — Job Migration Execution

## Purpose

This is where every prior phase's output converges into actual execution:
jobs move from on-prem to GCP, in a deliberately sequenced order, with
rigor proportional to their criticality tier. This folder is the
operational backbone of the migration — the tracker every status report
in [`00-project-overview/04-timeline-and-phases.md`](../00-project-overview/04-timeline-and-phases.md)
ultimately rolls up from.

## Owner

**Migration Program Lead**, executed by Data/Platform Engineering per
wave.

## Inputs

- Complete job inventory and criticality tiers from
  [`01-discovery/inventories/06-job-inventory.md`](../01-discovery/inventories/06-job-inventory.md)
  and
  [`01-discovery/inventories/02-business-critical-jobs.md`](../01-discovery/inventories/02-business-critical-jobs.md).
- Resolved dependency graphs from
  [`02-dependency-analysis/`](../02-dependency-analysis/README.md).
- Migrated, tested job code from
  [`07-spark-migration/`](../07-spark-migration/README.md) and
  [`09-composer-migration/`](../09-composer-migration/README.md).
- Provisioned infrastructure from
  [`13-infrastructure/`](../13-infrastructure/README.md).

## Outputs

- A wave plan sequencing every job's migration.
- A live migration tracker showing real-time status per job.
- Every job successfully cut over to GCP, validated, and stable.

## Prerequisites

[`13-infrastructure/`](../13-infrastructure/README.md) gated for the
relevant environment; the specific job's dependencies (per
[`02-dependency-analysis/`](../02-dependency-analysis/README.md)) already
migrated or scheduled in an earlier wave.

## Deliverables

1. Priority matrix (objective wave-assignment criteria).
2. Wave plan.
3. Migration tracker (living document/dashboard).
4. Parallel-run strategy.
5. Per-job execution steps.
6. Rollback procedures.
7. Production deployment checklist.

## Risks

Every risk documented throughout this repository converges here — this is
where a gap in dependency analysis, an unvalidated Hive migration, or an
untested rollback procedure actually manifests as a production incident if
missed earlier.

## Rollback

Every wave has an explicit, tested rollback path — see
[`06-rollback-procedures.md`](06-rollback-procedures.md). Rollback is
always available up until the on-prem decommissioning gate (per
[`05-storage-migration/07-rollback-procedure.md`](../05-storage-migration/07-rollback-procedure.md)).

## Validation

A job is not marked "migrated" in the tracker until it has passed: unit/
integration tests, data reconciliation, parallel-run comparison, and
Business Owner sign-off for Tier 1/2 jobs.

## Best Practices

Start with a small, low-risk pilot wave to prove the entire end-to-end
pattern (infrastructure, job code, DAG, validation, cutover, rollback)
before scaling to larger waves.

## Lessons Learned

Wave size should shrink, not grow, as tier increases — a Tier 1 wave of 2-3
jobs with maximum scrutiny is safer than a large batch cutover, even if
it's slower.

## Common Mistakes

- Sequencing waves purely by team convenience (whichever team is ready
  first) instead of the objective priority matrix, causing Tier 1 jobs to
  be rushed to meet an arbitrary wave deadline.
- Treating "code complete" as equivalent to "ready for cutover" — every
  gate in this folder (testing, validation, sign-off) must be independently
  satisfied.

## Production Notes

No Tier 1 job cutover is scheduled inside a charter freeze window — cross-
check every wave's proposed dates against
[`00-project-overview/02-migration-charter.md`](../00-project-overview/02-migration-charter.md)
before finalizing the wave plan.

---

## Folder structure

```
14-job-migration/
├── README.md                                   This file
├── 01-priority-matrix.md                        Objective wave-assignment criteria
├── 02-wave-planning.md                          The actual wave sequence
├── 03-migration-tracker.md                      Living per-job status tracker
├── 04-parallel-run-strategy.md                  Parallel-run design and duration per tier
├── 05-execution-steps-per-job.md                Standard per-job execution runbook
├── 06-rollback-procedures.md                    Wave and job-level rollback
└── 07-production-deployment-checklist.md         Final go/no-go checklist per job
```
