# Issue Management Process (Hypercare)

**Purpose:** Define how issues found during hypercare are triaged and
resolved with the elevated urgency appropriate to a still-stabilizing,
freshly-cutover job.
**Owner:** Migration Program Lead, executed by Platform/Data Engineering.

---

## Issue severity and response during hypercare

| Severity | Definition | Response Time (Hypercare) | Response Time (Standard Ops) |
|---|---|---|---|
| P1 | Job completely failing, data unavailable or clearly wrong | Immediate, all-hands | Standard on-call SLA |
| P2 | Job degraded (late, partial issue) but functioning | Same business day | Standard on-call SLA |
| P3 | Minor issue, cosmetic, or a non-blocking UAT-deferred item resurfacing | Within the week | Standard backlog |

Hypercare response times are tighter than standard operations, reflecting
the elevated attention and lower tolerance for unresolved issues during
this stabilization window.

## Issue investigation priority

Every hypercare issue is investigated with a bias toward finding the true
root cause, not just a quick symptom fix — since a recurring root cause
found now, before the job settles into "just how it works," is far
cheaper to fix than one discovered months later in standard operations.

## Daily hypercare stand-down review

For every job in active hypercare, a brief daily review (can be
async/dashboard-based for stable jobs, live for Tier 1) covers:

- Any new issue since the last review.
- Status of any open issue.
- Validation and SLA status.
- Whether exit criteria (per
  [`01-elevated-monitoring-plan.md`](01-elevated-monitoring-plan.md)) are
  trending toward being met.

## Feeding issues back into the broader program

Every hypercare issue is assessed for whether it's a **one-off** (specific
to this job) or indicates a **systemic gap** (a shared library issue, a
testing gap, a validation framework gap) that should inform how
subsequent waves' jobs are handled — logged in
[`documentation/`](../documentation/README.md) either way, with systemic
issues explicitly flagged for the Migration Program Lead's attention.

## Common Mistakes

- Treating every hypercare issue as an isolated fix without asking whether
  it reveals a pattern relevant to upcoming waves.
- Relaxing response time expectations too early in the hypercare window,
  before genuine stability is established.

## Production Notes

For Tier 1 jobs, any P1/P2 issue during hypercare should trigger an
explicit conversation about whether the hypercare clock should reset or
extend, per
[`01-elevated-monitoring-plan.md`](01-elevated-monitoring-plan.md) — this
decision should be made deliberately, not by default assumption in either
direction.
