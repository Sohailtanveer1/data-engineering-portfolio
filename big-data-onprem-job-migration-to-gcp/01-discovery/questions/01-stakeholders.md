# Discovery Questions — Executive & Product Stakeholders

**Purpose:** Establish the business context, priorities, and non-negotiable
constraints that every subsequent technical decision must respect. This
interview happens first because it sets the frame every other interview is
conducted within.
**Owner:** Migration Program Lead.
**Audience:** Executive Sponsor, VP Data/Engineering, Product leadership
with visibility into the roadmap the platform serves.
**Inputs:** Migration charter (draft), org chart.
**Outputs:** Confirmed priorities, confirmed freeze windows, confirmed
definition of "success," named escalation contacts.
**Format:** 60-minute structured interview, recorded/notes shared back to
interviewee for confirmation within 48 hours.

---

## Questions

| # | Question | Why we ask it |
|---|---|---|
| 1 | What does success look like for this migration, in your words — not the charter's? | Executives and the charter sometimes diverge on emphasis (e.g., charter says "functional parity," sponsor actually cares most about cost). Surfacing this early prevents a technically-successful migration that's perceived as a failure. |
| 2 | Which business functions would you personally escalate about if their data pipeline broke for a day? | This is a faster, more honest signal of true business-criticality than asking teams to self-report — it becomes an input to [`inventories/02-business-critical-jobs.md`](../inventories/02-business-critical-jobs.md). |
| 3 | Are there upcoming business events (new market launch, M&A, major promotional campaign) in the migration window we should know about? | These can create new freeze windows or new urgency the charter doesn't yet reflect. |
| 4 | What is the hard budget ceiling, and who approves an overrun? | Directly informs [`19-cost-optimization/`](../../19-cost-optimization/README.md) design constraints and the RACI escalation path. |
| 5 | Is there a hard deadline (contractual, compliance, board commitment) driving the timeline, or is timeline flexible if quality/safety require it? | Determines whether [`14-job-migration/`](../../14-job-migration/README.md) wave planning can trade schedule for safety, or must hold a fixed date. |
| 6 | Who outside of engineering must be kept informed of migration progress, and how often? | Feeds the communication plan in [`21-cutover/`](../../21-cutover/README.md) and the reporting cadence in [`00-project-overview/04-timeline-and-phases.md`](../../00-project-overview/04-timeline-and-phases.md). |
| 7 | Has a migration of this kind been attempted before at this company? What happened? | Prior attempts (even failed or partial ones) carry lessons and often leave behind half-migrated artifacts that Discovery needs to find. |
| 8 | What would make you personally veto or pause this migration mid-flight? | Establishes the sponsor's real risk tolerance, which should shape how conservative the wave/cutover plan is. |
| 9 | Are there regulatory or audit events (SOX audit, PCI assessment) scheduled during the migration window? | These can impose additional freeze windows or evidentiary requirements not yet in the charter. |
| 10 | Who is authorized to approve scope changes once the charter is signed? | Confirms the RACI's escalation path actually reflects real authority, not assumed authority. |

## Validation of answers

Cross-check freeze-window and business-criticality answers against the
independent Business interview
([`05-business.md`](05-business.md)) — executives and functional owners
sometimes disagree on what's truly critical, and both perspectives should be
reconciled explicitly, not silently averaged.
