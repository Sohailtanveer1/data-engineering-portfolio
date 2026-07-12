# Knowledge Transfer & Handover

**Purpose:** Formally transfer ownership from the migration team to
standing Operations — preventing the "everyone assumes someone else owns
this" gap flagged throughout this repository (e.g.,
[`16-data-validation/07-continuous-validation-in-production.md`](../16-data-validation/07-continuous-validation-in-production.md)).
**Owner:** Migration Program Lead (initiates), Operations Lead (accepts).

---

## Handover checklist

- [ ] Every runbook for this job's common failure modes exists in
      [`runbooks/`](../runbooks/README.md) and has been walked through
      with the receiving Operations team, not just handed over as a
      document.
- [ ] On-call rotation updated to include this job under standard (not
      migration-team-specific) coverage per
      [`18-monitoring/06-on-call-and-escalation.md`](../18-monitoring/06-on-call-and-escalation.md).
- [ ] Dashboard and alerting ownership transferred — Operations
      confirmed they know where to look and what "normal" looks like.
- [ ] Continuous validation ownership explicitly transferred per
      [`16-data-validation/07-continuous-validation-in-production.md`](../16-data-validation/07-continuous-validation-in-production.md).
- [ ] Cost/rightsizing review ownership transferred per
      [`19-cost-optimization/05-rightsizing-review-process.md`](../19-cost-optimization/05-rightsizing-review-process.md).
- [ ] Known open issues (non-blocking, from UAT or hypercare) documented
      and explicitly accepted by Operations as backlog items they now own.
- [ ] A named Operations contact confirmed as the ongoing point of
      accountability for this job.

## Handover session format

A live, hands-on session (not just document handoff) where the migration
team walks the Operations team through:

1. The job's architecture and key design decisions (referencing the
   relevant phase documents, e.g.,
   [`07-spark-migration/`](../07-spark-migration/README.md)).
2. A live walkthrough of the dashboards and what normal vs. abnormal
   looks like.
3. A walkthrough of at least one runbook, ideally with a simulated
   scenario.
4. Q&A — genuinely encouraged, not rushed through.

## Formal handover sign-off

The receiving Operations Lead formally confirms acceptance of ownership —
recorded in
[`documentation/`](../documentation/README.md), mirroring the rigor of
the UAT sign-off process in
[`20-uat/03-business-signoff-process.md`](../20-uat/03-business-signoff-process.md).

## Common Mistakes

- Treating handover as a document dump ("here's the wiki, good luck")
  instead of an active, hands-on transfer session.
- Transferring ownership before hypercare exit criteria are actually met,
  leaving Operations to handle a still-stabilizing job without the
  migration team's context.

## Production Notes

For Tier 1 jobs, schedule the handover session with enough lead time
before the migration team's attention shifts fully to the next wave —
a rushed, last-minute handover undermines its entire purpose.
