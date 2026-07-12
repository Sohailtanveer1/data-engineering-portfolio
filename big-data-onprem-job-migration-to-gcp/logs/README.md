# logs — Execution Logs

## Purpose

The archive of execution records referenced throughout this repository —
storage migration execution logs
([`05-storage-migration/02-distcp-migration-procedure.md`](../05-storage-migration/02-distcp-migration-procedure.md)),
rollback events
([`14-job-migration/06-rollback-procedures.md`](../14-job-migration/06-rollback-procedures.md)),
cutover records
([`21-cutover/01-go-live-plan.md`](../21-cutover/01-go-live-plan.md)),
and `prod` Terraform promotions
([`13-infrastructure/05-environment-promotion.md`](../13-infrastructure/05-environment-promotion.md)).
This is a manually-curated archive for significant, one-off events — not
a replacement for Cloud Logging (per
[`18-monitoring/01-logging-architecture.md`](../18-monitoring/01-logging-architecture.md)),
which captures routine operational logs automatically.

## Owner

Whoever executes the logged event — Platform Engineering, Migration
Program Lead, or Cloud/DevOps, depending on the event type.

## What gets logged here

| Event Type | Logged By | Referenced From |
|---|---|---|
| Storage migration execution | Platform Engineering | [`05-storage-migration/08-migration-execution-checklist.md`](../05-storage-migration/08-migration-execution-checklist.md) |
| Rollback (attempted or executed) | Migration Program Lead | [`14-job-migration/06-rollback-procedures.md`](../14-job-migration/06-rollback-procedures.md) |
| Cutover execution | Migration Program Lead | [`21-cutover/01-go-live-plan.md`](../21-cutover/01-go-live-plan.md) |
| `prod` Terraform apply (planned and emergency) | Cloud/DevOps | [`13-infrastructure/05-environment-promotion.md`](../13-infrastructure/05-environment-promotion.md) |
| Wave retrospective | Migration Program Lead | [`00-project-overview/04-timeline-and-phases.md`](../00-project-overview/04-timeline-and-phases.md) |

## Log entry format

Use [`log-entry-template.md`](log-entry-template.md) for every entry —
one file per event, named `YYYY-MM-DD-<short-description>.md`, organized
in this folder (optionally in dated subfolders once the volume warrants
it).

## Retention

Logs relevant to Tier 1 domains or compliance-relevant events (security
changes, data access) are retained per the audit retention requirement in
[`10-security/05-audit-logging.md`](../10-security/05-audit-logging.md) —
never deleted as routine cleanup.
