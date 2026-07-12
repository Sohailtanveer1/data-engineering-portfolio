# Business Sign-Off Process

**Purpose:** Formalize what "signed off" actually means — a specific,
documented, attributable decision, not an implied or assumed approval.
**Owner:** Migration Program Lead (process owner), Business Owner
(decision authority per the RACI).

---

## Sign-off requirements

| Job Tier | Sign-Off Required From | Format |
|---|---|---|
| Tier 1 | Named Business Owner | Written (email, ticket, or signed document) — verbal approval alone is insufficient given the compliance/audit relevance for Tier 1 domains |
| Tier 2 | Named Business Owner or delegate | Written |
| Tier 3 | Business Owner or delegate; may be a lighter-weight process | Written, can be a simple ticket comment |

## Sign-off record contents

Every sign-off record includes:

1. The specific job/domain being approved.
2. Confirmation that every acceptance criterion in
   [`01-acceptance-criteria.md`](01-acceptance-criteria.md) was reviewed.
3. Reference to the UAT session date and facilitator.
4. Any non-blocking issues acknowledged and accepted as post-cutover
   backlog (per
   [`04-issue-tracking-and-resolution.md`](04-issue-tracking-and-resolution.md)).
5. Explicit approval to proceed to cutover.

## What happens without sign-off

A job **cannot** proceed to
[`21-cutover/`](../21-cutover/README.md) without sign-off, per
[`14-job-migration/07-production-deployment-checklist.md`](../14-job-migration/07-production-deployment-checklist.md)
— this is a hard gate, not a recommendation. If a Business Owner is
unavailable or unresponsive, the Migration Program Lead escalates per the
RACI escalation path
([`00-project-overview/03-raci-matrix.md`](../00-project-overview/03-raci-matrix.md))
rather than proceeding without sign-off or indefinitely delaying with no
escalation.

## Sign-off record storage

Every sign-off record is stored in
[`documentation/`](../documentation/README.md) and referenced from
[`14-job-migration/03-migration-tracker.md`](../14-job-migration/03-migration-tracker.md)
— this is both an operational record and, for Tier 1 domains, potential
compliance evidence of due diligence.

## Common Mistakes

- Treating a verbal "looks good" in a meeting as equivalent to formal
  sign-off — always capture it in writing, even if the verbal approval
  came first.
- Proceeding to cutover based on an assumption that sign-off is "probably
  fine" when the Business Owner hasn't explicitly responded.

## Production Notes

For Tier 1 domains, obtain sign-off with enough lead time before the
planned cutover date to allow for last-minute issue resolution if
something surfaces — never obtain sign-off on the same day as cutover
itself.
