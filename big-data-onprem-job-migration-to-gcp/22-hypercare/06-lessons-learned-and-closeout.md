# Lessons Learned & Closeout

**Purpose:** Capture lessons learned in a durable, reusable form — feeding
back into this repository itself so subsequent waves (and any future
migration this company undertakes) benefit from what was learned, closing
the loop the "Lessons Learned" section in every phase document throughout
this repository anticipates.
**Owner:** Migration Program Lead.

---

## Lessons learned capture process

1. Aggregate findings from every
   [`05-post-implementation-review.md`](05-post-implementation-review.md)
   across all waves.
2. Categorize by phase (which numbered folder does this lesson relate to
   — e.g., "we should have caught this in
   [`02-dependency-analysis/`](../02-dependency-analysis/README.md),
   not discovered it during UAT").
3. For each significant lesson, propose a specific update to the relevant
   phase document in this repository — this repository is a living
   playbook, and lessons learned should improve it for whoever executes
   the next wave or the next migration.
4. Record lessons in
   [`documentation/`](../documentation/README.md) as a permanent record,
   independent of whether the corresponding phase document is updated
   immediately.

## Closeout checklist (per wave or full program)

- [ ] All jobs in scope have completed hypercare and been handed over to
      standing Operations.
- [ ] Post-implementation review completed and documented.
- [ ] Lessons learned captured and, where applicable, fed back into this
      repository's phase documents.
- [ ] Risk register (per
      [`00-project-overview/07-risk-register-summary.md`](../00-project-overview/07-risk-register-summary.md))
      updated to reflect resolved risks and any new risks identified for
      remaining waves.
- [ ] Cost actuals reconciled against baseline per
      [`19-cost-optimization/01-cost-baseline-and-attribution.md`](../19-cost-optimization/01-cost-baseline-and-attribution.md).
- [ ] For full program closeout: on-prem decommissioning plan confirmed
      and executed per
      [`05-storage-migration/07-rollback-procedure.md`](../05-storage-migration/07-rollback-procedure.md)
      decommissioning gate.

## Full program closeout

Once every wave has completed hypercare and the on-prem platform has been
decommissioned (or reduced to its agreed residual footprint per the
charter), the Migration Program Lead prepares a final program closeout
report for the Executive Sponsor, covering:

- Success criteria from
  [`00-project-overview/02-migration-charter.md`](../00-project-overview/02-migration-charter.md),
  confirmed met (or explicitly not met, with explanation).
- Final cost vs. budget.
- Consolidated lessons learned.
- Recommendations for ongoing platform operations beyond the migration
  program itself (transitioning fully into
  [`documentation/`](../documentation/README.md)-governed standard
  operations).

## Common Mistakes

- Letting the migration team disband before lessons learned are actually
  captured and fed back, losing the institutional knowledge gained.
- Treating program closeout as automatic once the last job cuts over,
  without the deliberate final review and decommissioning confirmation
  this document requires.

## Production Notes

This is the final document in the numbered phase sequence (00 through 22)
of this migration playbook — its completion, alongside the closeout
checklist above, marks the formal end of the migration program as a
distinct initiative, with the platform transitioning fully into standard,
ongoing operations governed by [`documentation/`](../documentation/README.md),
[`runbooks/`](../runbooks/README.md), and the monitoring/cost/security
disciplines established throughout this repository.
