# Discovery Questions — Operations / Production Support (NOC)

**Purpose:** The operations team sees the platform through the lens of
incidents, pages, and runbooks — a very different (and often more honest)
view of reliability than the platform or development teams provide. This
interview surfaces the real operational pain points the migration should
demonstrably fix.
**Owner:** Migration Program Lead, conducted with Operations/NOC lead.
**Audience:** Production support engineers, on-call rotation members, NOC
staff.

---

## Questions

| # | Question | Why we ask it |
|---|---|---|
| 1 | What are the top 5 recurring incident types on this platform over the last 12 months? | Directly identifies the pain points [`04-target-architecture/`](../../04-target-architecture/README.md) and [`18-monitoring/`](../../18-monitoring/README.md) should be explicitly designed to eliminate or catch earlier. |
| 2 | Which jobs page someone most frequently? | Frequently-paging jobs are strong candidates for extra validation and possibly earlier migration (to stop the pain sooner) or later migration (if too risky to touch early) — a call made explicitly, not by default. |
| 3 | What's the current mean time to detect (MTTD) and mean time to resolve (MTTR) for a failed job? | Sets the baseline that GCP-native monitoring/alerting in [`18-monitoring/`](../../18-monitoring/README.md) must beat, not just match. |
| 4 | Walk me through your current runbook for the most common failure — what do you actually do, step by step? | Existing runbooks are the seed for the new [`runbooks/`](../../runbooks/README.md) — better to adapt a proven process than write one from scratch. |
| 5 | Are there failure modes with no runbook — where resolution depends on a specific person's knowledge? | Single-person-dependency failure modes are a hidden risk (echoes R8) that must be documented before that person is unavailable. |
| 6 | What's the current on-call rotation and escalation path for this platform? | The new platform needs an equivalent (likely improved) on-call structure, designed deliberately in [`18-monitoring/`](../../18-monitoring/README.md) and [`22-hypercare/`](../../22-hypercare/README.md), not left undefined until go-live. |
| 7 | How do you currently know a job succeeded vs. silently produced wrong/incomplete data? | Silent failures are the most dangerous category — reveals whether current validation is sufficient or whether [`16-data-validation/`](../../16-data-validation/README.md) needs to close a real existing gap, not just replicate current practice. |
| 8 | What tools do you use today to investigate an incident (logs, dashboards, ad-hoc queries)? | Sets the functional bar for what Cloud Logging/Monitoring dashboards in [`18-monitoring/`](../../18-monitoring/README.md) must replicate or improve on. |
| 9 | Are there jobs that require manual restart/intervention as a normal (not exceptional) part of operating them? | These are prime candidates for the idempotency and retry-logic redesign work in [`07-spark-migration/`](../../07-spark-migration/README.md) — "normal manual intervention" should not survive the migration. |
| 10 | What would make hypercare (the post-cutover stabilization period) feel successful to you, specifically? | Directly informs the design of [`22-hypercare/`](../../22-hypercare/README.md) from the perspective of the team who will actually staff it. |

## Validation of answers

Cross-reference stated incident frequency and MTTR against actual incident
tickets/paging system history where available, rather than relying purely
on recollection.
