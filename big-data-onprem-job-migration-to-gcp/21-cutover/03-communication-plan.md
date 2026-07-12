# Communication Plan

**Purpose:** Ensure every stakeholder knows what's happening, when, and
what to expect — preventing the confusion and unplanned interference that
under-communicated cutovers commonly cause.
**Owner:** Migration Program Lead / Communications Lead.

---

## Communication timeline

| Timing | Audience | Message |
|---|---|---|
| T-2 weeks | All stakeholders (per RACI) | Cutover scheduled, expected impact (if any), freeze window begins |
| T-1 week | Business Owner, Data Consumers | Reminder, confirm no last-minute concerns |
| T-1 day | All stakeholders | Final go/no-go confirmed, cutover proceeding |
| T-0 (during) | Command center channel | Real-time status updates per [`02-command-center-operations.md`](02-command-center-operations.md) |
| T+0 (immediately after) | All stakeholders | Cutover complete, validation status |
| T+1 day | All stakeholders | Post-cutover stability update |
| T+hypercare end | All stakeholders | Formal hypercare close, per [`22-hypercare/`](../22-hypercare/README.md) |

## Audience-specific messaging

| Audience | What They Need to Know |
|---|---|
| Executive Sponsor | High-level status, any risk to timeline/budget |
| Business Owner | Direct impact to their function, any action needed on their part |
| Data Consumers (analysts, BI users) | Any temporary access disruption, new connection details if applicable |
| Operations/on-call | Technical details needed to support the cutover and respond to any issue |
| Downstream/partner teams | Any change to data availability timing or format they depend on |

## Communication channels

- **Status page or shared tracker** (per
  [`14-job-migration/03-migration-tracker.md`](../14-job-migration/03-migration-tracker.md))
  for anyone wanting self-service status.
- **Direct notification** (email/Slack) for anyone requiring proactive
  communication, not just self-service access.
- **Command center channel** for real-time coordination among active
  participants only, not broadcast broadly.

## Common Mistakes

- Sending a single generic announcement to everyone instead of tailoring
  the message to what each audience actually needs to know and do.
- Going silent during the cutover window itself, leaving stakeholders to
  wonder about status — the T-0 real-time cadence exists specifically to
  prevent this.

## Production Notes

For Tier 1 cutovers affecting a customer-facing function (pricing,
inventory availability), coordinate the communication timeline with
Marketing/Merchandising to ensure no conflicting customer-facing
announcement or promotional activity is planned for the same window.
