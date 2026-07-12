# 02 — Dependency Analysis

## Purpose

[`01-discovery/`](../01-discovery/README.md) produced a job inventory — a
flat list of what runs. This phase produces the **dependency graph** — how
everything connects. A flat inventory tells you 400 jobs exist; a
dependency graph tells you that migrating `pricing_nightly_batch` before
`inventory_sync_intraday` will break it, and that `legacy_vendor_feed_2019`
is quietly the only source of a lookup table three other Tier 1 jobs read
from. This is the single most effective phase for preventing the
"unknown dependency caused a production incident" failure mode that sinks
migrations of this size.

## Owner

**Migration Program Lead**, executed by **Platform Engineering** and
**Data Engineering**, using static analysis of code/config plus targeted
follow-up with the developers interviewed in
[`01-discovery/questions/06-developers.md`](../01-discovery/questions/06-developers.md).

## Inputs

- Complete job inventory from [`01-discovery/inventories/06-job-inventory.md`](../01-discovery/inventories/06-job-inventory.md).
- Read access to all job source code repositories, shell scripts, and
  scheduler definitions.
- Read access to HDFS (for path-based dependency discovery) and the Hive
  Metastore.

## Outputs

- A completed dependency graph — visual and tabular — for every in-scope
  job.
- A prioritized list of dependencies with no confirmed owner, requiring
  resolution before that job can be scheduled into a wave.
- Updated risk register entries for any dependency discovered to be more
  fragile or more widely relied-upon than assumed during Discovery.

## Prerequisites

Phase 01 gated — see
[`00-project-overview/04-timeline-and-phases.md`](../00-project-overview/04-timeline-and-phases.md).
The job inventory must exist before dependency analysis can be scoped
against it.

## Deliverables

1. Nine dependency-identification methodology documents in
   [`methodology/`](methodology/), one per dependency category, each
   explaining exactly how to find that category of dependency in this
   environment — not generic advice, but the actual commands/techniques to
   run against this platform.
2. Three reusable templates in [`templates/`](templates/) — a dependency
   graph template, a per-job dependency card, and a dependency matrix
   inventory — used to capture findings consistently across every job.
3. A completed dependency matrix (built from the templates) covering every
   job in the job inventory.

## Risks

- **False confidence from partial analysis.** Running one technique (e.g.,
  static grep for hostnames) and declaring dependency analysis "done"
  misses dependencies only visible through another technique (e.g., a
  Hive table only ever referenced by a downstream BI tool's saved query,
  invisible to code analysis). This is why nine distinct methodologies are
  used together, not just one.
- **Dependency graphs going stale.** A dependency graph built once at the
  start of a program spanning months will not reflect reality by the time
  a job's wave comes up. See "Refresh cadence" in each methodology
  document.

## Rollback

N/A — this phase is read-only analysis against the source platform.

## Validation

A job is not considered to have a validated dependency graph until it has
been checked against **at least two independent techniques** from the
methodology documents (e.g., static code analysis *and* developer
confirmation; or HDFS access log analysis *and* Metastore query log
analysis). Single-technique dependency mapping is not sufficient for Tier 1
jobs.

## Best Practices

- Automate what can be automated (JAR manifest inspection, hostname
  grepping, HDFS access log parsing) and reserve human interview time for
  what can't (business logic embedded in conditional workflow branches,
  "why does this job exist" questions).
- Build the dependency graph in a format that can be diffed over time
  (structured data, not just prose) so drift is detectable, not just
  assumed away.

## Lessons Learned

The dependencies that cause production incidents are almost never the ones
anyone was worried about — they're the boring, unglamorous ones nobody
thought to ask about (a shared lookup table, a shell script sourcing a
common environment file, a downstream analyst's saved query against a
table everyone assumed was internal-only).

## Common Mistakes

- Scoping dependency analysis only to *upstream* dependencies (what a job
  reads) and neglecting *downstream* consumers (who reads what a job
  produces) — see
  [`methodology/09-downstream-consumer-analysis.md`](methodology/09-downstream-consumer-analysis.md).
  Downstream breakage is actually the more common production incident
  pattern, because upstream dependencies are usually where developers
  focus their own understanding already.
- Treating dependency analysis as a one-time exercise instead of a living
  artifact refreshed before each migration wave.

## Production Notes

For Tier 1 jobs (per
[`01-discovery/inventories/02-business-critical-jobs.md`](../01-discovery/inventories/02-business-critical-jobs.md)),
dependency graphs must be re-validated within 2 weeks of that job's
scheduled migration wave, not relied upon from months-old Discovery-phase
analysis — the platform changes continuously even during the migration
program itself.

---

## Folder structure

```
02-dependency-analysis/
├── README.md                                            This file
├── methodology/                                          How to find each category of dependency
│   ├── 01-spark-job-dependencies.md
│   ├── 02-hive-dependencies.md
│   ├── 03-jar-library-shared-utility-dependencies.md
│   ├── 04-shell-script-and-cron-dependencies.md
│   ├── 05-scheduler-workflow-dependencies.md
│   ├── 06-kafka-dependencies.md
│   ├── 07-database-and-rest-api-dependencies.md
│   ├── 08-file-and-filesystem-dependencies.md            FTP/SFTP/NFS/HDFS
│   └── 09-downstream-consumer-analysis.md
└── templates/                                             Reusable capture templates
    ├── 01-dependency-graph-template.md
    ├── 02-job-dependency-card-template.md
    └── 03-dependency-matrix-inventory-template.md
```
