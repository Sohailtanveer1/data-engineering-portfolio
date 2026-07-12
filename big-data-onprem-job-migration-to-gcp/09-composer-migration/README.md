# 09 — Scheduler Migration (Cloud Composer)

## Purpose

Convert every orchestration mechanism found in
[`01-discovery/inventories/10-scheduler-inventory.md`](../01-discovery/inventories/10-scheduler-inventory.md)
— Oozie, cron, and any partially-adopted Airflow — into a single,
consistent Cloud Composer implementation, following the orchestration
architecture defined in
[`04-target-architecture/06-orchestration-architecture.md`](../04-target-architecture/06-orchestration-architecture.md).
This is a deliberate redesign of orchestration logic, not a mechanical
XML-to-Python translation — see the scheduler dependency analysis in
[`02-dependency-analysis/methodology/05-scheduler-workflow-dependencies.md`](../02-dependency-analysis/methodology/05-scheduler-workflow-dependencies.md)
for why conditional/branching logic in particular requires careful,
intentional translation.

## Owner

**Platform Engineering**, with each job family's DAG reviewed by its
owning Data Engineering team.

## Inputs

- Full scheduler inventory and dependency graphs from
  [`01-discovery/inventories/10-scheduler-inventory.md`](../01-discovery/inventories/10-scheduler-inventory.md)
  and
  [`02-dependency-analysis/methodology/05-scheduler-workflow-dependencies.md`](../02-dependency-analysis/methodology/05-scheduler-workflow-dependencies.md).
- Orchestration architecture from
  [`04-target-architecture/06-orchestration-architecture.md`](../04-target-architecture/06-orchestration-architecture.md).
- Migrated, tested Spark jobs from
  [`07-spark-migration/`](../07-spark-migration/README.md) (DAGs
  orchestrate jobs; the jobs themselves must already exist and be
  independently tested).

## Outputs

- Every scheduled job (Oozie, cron, ad-hoc) represented as a Composer DAG,
  organized by business domain per the target architecture.
- A dynamic DAG generation pattern for job families with many
  structurally-similar DAGs.
- Monitoring, retry, and alerting configured consistently across every DAG.

## Prerequisites

[`04-target-architecture/`](../04-target-architecture/README.md) gated;
[`07-spark-migration/`](../07-spark-migration/README.md) substantially
underway (a DAG needs a real, tested job to orchestrate).

## Deliverables

1. Oozie-to-Composer conversion procedure, preserving conditional/
   branching logic explicitly.
2. Cron/shell-to-Composer conversion procedure.
3. Dynamic DAG generation pattern and reference implementation.
4. DAG authoring best practices standard.
5. Monitoring, retry, and alerting configuration standard.
6. Variables, Connections, and Secrets management standard.

## Risks

- **Losing conditional/branching logic** during Oozie decision-node
  translation — the highest-risk category per
  [`02-dependency-analysis/methodology/05-scheduler-workflow-dependencies.md`](../02-dependency-analysis/methodology/05-scheduler-workflow-dependencies.md).
- **Data-availability triggers force-fit into pure time schedules**,
  causing jobs to run before their real input data has landed.
- **DAG sprawl** — hundreds of near-identical, hand-copied DAGs instead of
  a dynamic generation pattern, making maintenance and consistency
  unmanageable at scale.

## Rollback

A DAG can be paused in Composer without affecting the on-prem Oozie/cron
job, which continues running per constraint C7 — see
[`14-job-migration/`](../14-job-migration/README.md) for job-level
rollback coordination.

## Validation

Every DAG must be validated to trigger its underlying job(s) at the
correct time, in the correct order, respecting the correct
dependency/data-availability conditions — validated via
[`15-testing/`](../15-testing/README.md) DAG-level integration testing,
not just "the DAG parses without error."

## Best Practices

Build the dynamic DAG generation pattern early and use it for every
structurally-similar job family — see
[`03-dynamic-dag-generation.md`](03-dynamic-dag-generation.md).

## Lessons Learned

Oozie coordinators that "just run on a schedule" on the surface frequently
have a data-availability check embedded in a preceding decision node or
shell action that's easy to miss if the translation only looks at the
coordinator's declared frequency tag.

## Common Mistakes

- Copying Oozie's schedule frequency into a Composer `schedule_interval`
  without checking for an embedded data-availability precondition.
- Writing one hand-crafted DAG file per job for a large family of
  structurally identical jobs instead of using dynamic DAG generation,
  creating unmaintainable duplication.

## Production Notes

For Tier 1 job DAGs, explicitly test the failure and retry path (not just
the happy path) in a non-production Composer environment before that DAG
is used for the job's actual cutover.

---

## Folder structure

```
09-composer-migration/
├── README.md                                       This file
├── 01-oozie-to-composer-conversion.md               Preserving conditional/branching logic
├── 02-cron-and-shell-to-composer-conversion.md      Converting cron/shell to DAGs
├── 03-dynamic-dag-generation.md                     Pattern + reference implementation
├── 04-dag-best-practices.md                          Authoring standard
├── 05-monitoring-retries-and-alerts.md               Consistent operational configuration
├── 06-variables-connections-and-secrets.md            Configuration management standard
└── examples/                                          Working DAG code
    ├── README.md
    ├── pricing_nightly_batch_dag.py                  Production DAG example
    └── dynamic_dag_factory.py                        Dynamic DAG generation example
```
