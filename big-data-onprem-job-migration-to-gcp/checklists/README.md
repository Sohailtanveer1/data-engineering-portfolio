# checklists — Cross-Phase Checklists

## Purpose

Master, consolidated checklists that pull together gates from multiple
phase folders — distinct from the many phase-specific execution
checklists already embedded within individual phases (e.g.,
[`05-storage-migration/08-migration-execution-checklist.md`](../05-storage-migration/08-migration-execution-checklist.md),
[`14-job-migration/07-production-deployment-checklist.md`](../14-job-migration/07-production-deployment-checklist.md)).
These are used when someone needs the full, cross-cutting picture rather
than a single phase's slice of it.

## Owner

Migration Program Lead.

## Contents

| Checklist | Use When |
|---|---|
| [`production-readiness-checklist.md`](production-readiness-checklist.md) | Confirming a GCP environment is genuinely ready for production data, consolidating gates from `10-security`, `11-network`, `12-cluster-design`, `13-infrastructure`, `18-monitoring` |
| [`migration-checklist.md`](migration-checklist.md) | The master, single-page view of every gate a job passes through end-to-end, for a quick reference without navigating every individual phase checklist |
