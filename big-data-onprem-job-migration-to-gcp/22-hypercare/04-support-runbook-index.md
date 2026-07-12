# Support Runbook Index

**Purpose:** The navigational index into [`runbooks/`](../runbooks/README.md)
specifically from a hypercare/support perspective — helping an on-call
engineer (migration-team or standing Operations) find the right runbook
fast during an active issue.
**Owner:** Platform Engineering.

---

## How this differs from `runbooks/`

[`runbooks/`](../runbooks/README.md) is the actual, complete runbook
library used platform-wide. This document is a **hypercare-specific
lens** on it — surfacing the runbooks most relevant during the
stabilization period specifically, and noting any hypercare-specific
runbook that doesn't yet have a permanent home in the standard library.

## Most-referenced runbooks during hypercare

| Scenario | Runbook |
|---|---|
| Job failed, need to diagnose | [`runbooks/`](../runbooks/README.md) — job failure diagnosis runbook |
| Data validation failure | [`runbooks/`](../runbooks/README.md) — validation failure investigation runbook |
| Need to execute a rollback | [`21-cutover/06-rollback-plan.md`](../21-cutover/06-rollback-plan.md) |
| Cluster stuck / orphaned | [`runbooks/`](../runbooks/README.md) — orphaned cluster cleanup runbook |
| Alert fired, unclear what it means | [`18-monitoring/03-alerting-strategy.md`](../18-monitoring/03-alerting-strategy.md) alert catalog, cross-referenced to the specific runbook |

## Building missing runbooks during hypercare

If an issue arises during hypercare with **no existing runbook**, this is
itself a hypercare deliverable: write the runbook as part of resolving the
issue, not just fix it ad hoc and move on. This directly grows
[`runbooks/`](../runbooks/README.md) based on real, encountered scenarios
rather than only speculative ones anticipated in advance.

## Runbook quality bar for hypercare handover

Before knowledge transfer (per
[`03-knowledge-transfer-and-handover.md`](03-knowledge-transfer-and-handover.md))
is considered complete, every runbook referenced above must be:

- Actually usable by someone without deep migration-team context (written
  for a standing Operations engineer, not just the person who wrote it).
- Walked through at least once with the receiving team, not just handed
  over as a document.

## Common Mistakes

- Resolving a novel issue during hypercare via tribal knowledge (a Slack
  thread, a verbal explanation) without writing it up as a runbook —
  reproducing exactly the undocumented-knowledge risk (R8) this migration
  set out to avoid.
- Writing runbooks only from the migration team's perspective, assuming
  context the receiving Operations team won't have.

## Production Notes

Track runbook creation as an explicit hypercare metric — the number of
new runbooks written during a job's hypercare period is a useful
indicator of how much genuinely novel operational knowledge that job
required, informing future wave planning effort estimates.
