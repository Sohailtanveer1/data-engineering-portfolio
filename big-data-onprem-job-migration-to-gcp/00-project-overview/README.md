# 00 — Project Overview

## Purpose

This folder is the entry point for the entire migration program. Anyone new
to the engagement — a newly onboarded engineer, an auditor, a VP asked to
approve budget, a new stakeholder from the business — should be able to read
every document in this folder in under an hour and come away understanding:
what is being migrated, why, by when, who is accountable for what, what
"done" means, and what could derail it.

## Owner

**Migration Program Lead** (Principal Data Platform Engineer or Engineering
Manager assigned to own the migration end-to-end). This folder is the
program lead's responsibility to keep current; it is reviewed at every
phase gate (see [`04-timeline-and-phases.md`](04-timeline-and-phases.md)).

## How this folder is used

| Document | Read this when you need to... |
|---|---|
| [`01-executive-summary.md`](01-executive-summary.md) | Brief an executive or new stakeholder in 5 minutes |
| [`02-migration-charter.md`](02-migration-charter.md) | Know exactly what's in scope, out of scope, and how success is measured |
| [`03-raci-matrix.md`](03-raci-matrix.md) | Know who to contact for a decision, an approval, or a status update |
| [`04-timeline-and-phases.md`](04-timeline-and-phases.md) | Know what phase we're in, what gates it, and what's next |
| [`05-glossary.md`](05-glossary.md) | Look up a term that's ambiguous between on-prem and GCP vocabularies |
| [`06-assumptions-and-constraints.md`](06-assumptions-and-constraints.md) | Understand what we're assuming to be true, and what limits our options |
| [`07-risk-register-summary.md`](07-risk-register-summary.md) | See the top program-level risks at a glance (full register lives in [`documentation/`](../documentation/README.md)) |

## Inputs

- Executive sponsorship and a funded budget line for the migration.
- A named Migration Program Lead with authority to make cross-team decisions.
- Access to the current on-prem platform (for the assessment phases that
  follow this one).

## Outputs

- A signed-off charter that every subsequent phase is scoped against.
- A RACI matrix that resolves "who approves this" questions before they
  become blockers mid-migration.
- A phase-gated timeline used to report status upward and to trigger
  go/no-go decisions between phases.

## Prerequisites

None — this is the first folder in the program. Everything downstream
depends on the documents here being signed off first.

## Deliverables

1. Executive summary (approved by sponsor)
2. Migration charter (approved by sponsor + platform + security leads)
3. RACI matrix (circulated to all named parties)
4. Phase timeline with gate criteria
5. Glossary (living document, updated as terms surface)
6. Assumptions & constraints log
7. Risk register summary

## Validation

This folder is "done" when the charter, RACI, and timeline have been
reviewed and explicitly approved (email, ticket, or signed doc — not just
"nobody objected") by: the executive sponsor, the platform engineering lead,
the security lead, and the business stakeholder owning the most
business-critical jobs identified in [`01-discovery/`](../01-discovery/README.md).

## Common Mistakes

- **Starting technical work before the charter is approved.** Engineers are
  eager to start migrating storage or Spark jobs before scope is agreed.
  This routinely causes rework when "in scope" turns out to be contested
  later (e.g., "we assumed the fraud-detection Spark jobs were out of
  scope, the business assumed they were in scope").
- **Treating the RACI as a formality.** In every migration of this size,
  there is at least one moment where a decision stalls for days because
  nobody was sure who could approve it. The RACI matrix exists specifically
  to prevent that — keep it accurate, not just present.
- **Writing the timeline as a single Gantt chart with no gates.** Without
  explicit phase-gate exit criteria, "in progress" phases silently slip
  and nobody notices until cutover is at risk.

## Production Notes

For an ecommerce company specifically: the charter and timeline must be
built around **peak trading calendar** (Black Friday / Cyber Monday, end of
quarter, major promotional events, regional sale days). See
[`02-migration-charter.md`](02-migration-charter.md) for the explicit
change-freeze windows this program commits to.
