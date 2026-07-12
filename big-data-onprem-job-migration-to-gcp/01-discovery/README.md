# 01 — Discovery & Assessment

## Purpose

Before a single job is migrated, we must know exactly what exists, who
depends on it, how well it currently performs against business
expectations, and what constraints (legal, technical, operational) bound
our options. Discovery is the phase where "we think we have about 300 Spark
jobs" becomes "we have 287 Spark jobs, of which 41 are business-critical,
running on Spark 2.4.8, with these 6 having no owner we can currently
identify." Every subsequent phase in this repository depends on Discovery
being thorough — a migration built on an incomplete inventory *will*
rediscover missing dependencies in production, at the worst possible time.

## Owner

**Migration Program Lead**, executing through **Platform Engineering** and
**Data Engineering**, with mandatory input from every group listed in
[`questions/`](questions/).

## Inputs

- Charter and RACI from [`00-project-overview/`](../00-project-overview/README.md).
- Access (read-only is sufficient) to the on-prem cluster: HDFS, Hive
  Metastore, YARN Resource Manager, the scheduler (Oozie/Airflow/cron), and
  any job-scheduling/ticketing system used to track job ownership.
- Calendar access to schedule interviews with each stakeholder group.

## Outputs

- Answered question sets for all 8 stakeholder groups in
  [`questions/`](questions/), each with named respondents and dates.
- 12 completed inventories in [`inventories/`](inventories/) covering SLAs,
  business-critical jobs, peak/downtime windows, retention/compliance,
  DR/RPO/RTO, and full job/application/Spark/Hive/scheduler/storage/external
  dependency inventories.

## Prerequisites

- Charter approved (see [`00-project-overview/02-migration-charter.md`](../00-project-overview/02-migration-charter.md)).
- Named contacts for each stakeholder group (part of the RACI in
  [`00-project-overview/03-raci-matrix.md`](../00-project-overview/03-raci-matrix.md)).

## Deliverables

1. Eight completed stakeholder question-and-answer documents.
2. Twelve completed inventory documents (job, application, Spark, Hive,
   scheduler, storage, external dependencies, SLAs, business-critical jobs,
   peak/downtime windows, retention/compliance, DR/RPO/RTO).
3. An updated [`00-project-overview/06-assumptions-and-constraints.md`](../00-project-overview/06-assumptions-and-constraints.md)
   with every assumption confirmed or corrected.

## Risks

- **Interview fatigue / stakeholder unavailability** stretching this phase
  indefinitely. Mitigate with tightly scoped interviews (60–90 min per
  group) using the pre-written question sets below rather than open-ended
  discovery sessions.
- **Self-reported inventories being wrong.** Humans misremember what's
  running. Every self-reported inventory in this phase must be
  cross-validated against actual cluster telemetry (YARN application
  history, Hive Metastore query logs, crontab/Oozie coordinator XML) before
  being trusted — see the validation note in each inventory document.
- **Political sensitivity of "business-critical" labeling.** Every team
  believes their job is critical. The business-critical-jobs inventory
  defines objective criteria specifically to defuse this.

## Rollback

N/A — Discovery is read-only against the source platform. No production
system is modified during this phase.

## Validation

Every inventory in this folder must be cross-validated against at least one
independent source of truth (cluster logs, scheduler metadata, Metastore
queries) — not accepted on interview testimony alone. See the "Validation
method" section within each inventory document.

## Best Practices

- Run stakeholder interviews **before** building inventories from logs —
  the interviews tell you what to look for; the logs tell you the ground
  truth. Reconcile discrepancies explicitly rather than picking one source
  blindly.
- Timebox this phase. Discovery has no natural end state — there is always
  one more thing to investigate. Set an explicit exit date at kickoff, and
  treat anything discovered after the gate as a controlled backlog item, not
  a phase re-open, unless it's a business-critical gap.

## Lessons Learned

Migrations that skip or rush Discovery consistently rediscover critical
dependencies during `07-spark-migration/` or, worse, during
`21-cutover/` — at which point the fix is far more expensive and far more
visible.

## Common Mistakes

- Interviewing only engineering teams and skipping Business/Data Consumers
  (see [`questions/05-business.md`](questions/05-business.md) and
  [`questions/08-data-consumers.md`](questions/08-data-consumers.md)) —
  this is the single most common gap, and it's the one that causes UAT
  surprises in [`20-uat/`](../20-uat/README.md).
- Treating the job inventory as a one-time export. Jobs get added and
  removed on-prem throughout the program; the inventory needs a refresh
  checkpoint before [`14-job-migration/`](../14-job-migration/README.md)
  wave planning locks in.

## Production Notes

For an ecommerce platform, pay particular attention to
[`inventories/03-peak-hours-and-downtime-windows.md`](inventories/03-peak-hours-and-downtime-windows.md)
and [`inventories/02-business-critical-jobs.md`](inventories/02-business-critical-jobs.md)
— these directly gate the freeze windows in the charter and the wave
sequencing in `14-job-migration/`.

---

## Folder structure

```
01-discovery/
├── README.md                              This file
├── questions/                              What to ask each stakeholder group, and why
│   ├── 01-stakeholders.md                  Executive/product stakeholders
│   ├── 02-platform-team.md                 On-prem Hadoop/platform admins
│   ├── 03-security-team.md                 InfoSec / security engineering
│   ├── 04-networking-team.md               Network engineering
│   ├── 05-business.md                      Business function owners
│   ├── 06-developers.md                    Engineers who write/own jobs
│   ├── 07-operations.md                    Production support / NOC
│   └── 08-data-consumers.md                Analysts, BI, downstream teams
└── inventories/                            What we must document about the current state
    ├── 01-sla-inventory.md
    ├── 02-business-critical-jobs.md
    ├── 03-peak-hours-and-downtime-windows.md
    ├── 04-data-retention-and-compliance.md
    ├── 05-disaster-recovery-rpo-rto.md
    ├── 06-job-inventory.md
    ├── 07-application-inventory.md
    ├── 08-spark-inventory.md
    ├── 09-hive-inventory.md
    ├── 10-scheduler-inventory.md
    ├── 11-storage-inventory.md
    └── 12-external-dependencies.md
```

Reusable blank versions of every inventory table in this folder are also
available as importable templates in [`templates/`](../templates/README.md)
for teams that prefer to fill them in via spreadsheet.
