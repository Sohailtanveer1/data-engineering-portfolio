# Migration Tracker

**Purpose:** The single, live source of truth for every job's migration
status — referenced by status reporting
([`00-project-overview/04-timeline-and-phases.md`](../00-project-overview/04-timeline-and-phases.md))
and by every phase folder's "recorded complete in the tracker" gate.
**Owner:** Migration Program Lead, updated by whoever executes each job's
migration step.

---

## Tracker schema

In practice this tracker should be a live spreadsheet or project-tracking
board (Jira/Linear/Sheets), not a static markdown table — the schema below
defines its required columns regardless of tooling:

| Column | Purpose |
|---|---|
| Job ID | Links to [`01-discovery/inventories/06-job-inventory.md`](../01-discovery/inventories/06-job-inventory.md) |
| Criticality Tier | From [`01-discovery/inventories/02-business-critical-jobs.md`](../01-discovery/inventories/02-business-critical-jobs.md) |
| Wave | From [`02-wave-planning.md`](02-wave-planning.md) |
| Dependency Analysis Status | Complete / In Progress / Blocked |
| Storage Migration Status | Not Started / In Progress / Validated |
| Data Migration Status | Not Started / In Progress / Reconciled |
| Hive Migration Status (if applicable) | Not Started / In Progress / Validated |
| Spark Migration Status | Not Started / Code Complete / Tested |
| Composer DAG Status | Not Started / Built / Tested |
| Security Review Status | Not Started / In Progress / Approved |
| Parallel-Run Status | Not Started / In Progress / Passed / Failed |
| UAT Status (Tier 1/2 only) | Not Started / In Progress / Signed Off |
| Cutover Status | Not Scheduled / Scheduled / Complete / Rolled Back |
| Owner | Named individual accountable for this job's migration |
| Blockers | Free text, current blocking issue if any |
| Last Updated | Date |

## Status roll-up view

A derived, aggregated view (built from the detailed tracker) for reporting
upward:

| Wave | Total Jobs | Complete | In Progress | Blocked | Not Started |
|---|---|---|---|---|---|
| Wave 0 | 2 | 2 | 0 | 0 | 0 |
| Wave 1 | 8 | 5 | 2 | 1 | 0 |
| Wave 2 | 10 | 0 | 0 | 0 | 10 |

## Definition of "Complete" for a job

A job is only marked fully "Complete" in the tracker when **every** status
column above reads its terminal successful state — partial completion
(e.g., "code complete" but "parallel-run not started") is not rounded up
to "Complete" for reporting purposes, even under schedule pressure.

## Update cadence

- Updated by the executing engineer immediately after completing each
  phase step for a job (not batched at end of week) — a stale tracker
  defeats its purpose as a real-time coordination tool.
- Reviewed by the Migration Program Lead daily during active wave
  execution.

## Common Mistakes

- Allowing the tracker to diverge from reality because updates are
  batched or forgotten — treat tracker updates as part of "done," not an
  optional follow-up.
- Marking a job "Complete" based on code/config completion alone, skipping
  the validation and sign-off columns.

## Production Notes

For Tier 1 jobs, the tracker's "Blockers" field must never be left blank
while any status column is non-terminal — if a Tier 1 job's status hasn't
advanced in more than 2 business days, either a blocker is documented or
the Program Lead should be actively asking why.
