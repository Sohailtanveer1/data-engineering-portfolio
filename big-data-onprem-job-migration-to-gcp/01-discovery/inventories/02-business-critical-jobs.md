# Business-Critical Jobs Inventory

**Purpose:** Every team believes their job is critical. This document
exists to convert that subjective claim into an objective, defensible tier
assignment that drives wave sequencing, freeze-window protection, and
validation rigor — consistently, not politically.
**Owner:** Migration Program Lead, ratified by the Executive Sponsor and
affected Business Owners (per RACI).
**Inputs:** [`questions/01-stakeholders.md`](../questions/01-stakeholders.md)
and [`questions/05-business.md`](../questions/05-business.md) interview
results, [`06-job-inventory.md`](06-job-inventory.md).
**Outputs:** Directly drives wave prioritization in
[`14-job-migration/`](../../14-job-migration/README.md) and freeze-window
enforcement from the charter.
**Validation method:** Every Tier 1 classification must be corroborated by
*both* a business interview and an objective signal (revenue linkage,
regulatory requirement, or documented past incident impact) — a single
person's assertion is not sufficient to assign Tier 1.

---

## Criticality tier definitions

| Tier | Definition | Wave placement rule |
|---|---|---|
| **Tier 1 — Business-Critical** | Direct, same-day impact on revenue, regulatory compliance, fraud/security posture, or customer-facing operations if late or wrong | Migrated last, only after the pattern is proven on Tier 2/3 jobs; mandatory parallel-run before cutover; never scheduled inside a freeze window |
| **Tier 2 — Business-Important** | Impacts a business function's efficiency or decision quality within days, but has a manual workaround or delayed-impact tolerance | Migrated in the middle waves; parallel-run recommended but duration can be shorter |
| **Tier 3 — Standard** | Internal analytics, ad-hoc reporting, non-time-sensitive batch jobs | Migrated first, used to prove the migration pattern and tooling |
| **Tier 4 — Candidate for Retirement** | No confirmed active consumer identified during Discovery | Not migrated by default — confirmed retirement candidate, revisited at the end of Discovery before being dropped |

## Objective criteria for Tier 1 assignment

A job qualifies for Tier 1 if it meets **at least one** of:

1. Directly feeds a customer-facing system (checkout, pricing display,
   inventory availability) within a 1-hour latency window.
2. Feeds fraud detection or security-relevant decisioning.
3. Feeds a regulatory or contractual reporting obligation with a hard
   deadline (e.g., SOX financial close).
4. Has a documented historical incident where its failure caused a
   measurable revenue or compliance impact.
5. The Executive Sponsor personally named it in
   [`questions/01-stakeholders.md`](../questions/01-stakeholders.md) Q2.

## Inventory

| Job ID | Job Name | Business Function | Tier | Justification (which criterion above) | Confirmed by (name/role) | Date confirmed |
|---|---|---|---|---|---|---|
| EX-001 | `pricing_nightly_batch` | Pricing | Tier 1 | Criterion 1 — feeds storefront pricing display | Merchandising Director | _(fill in)_ |
| EX-002 | `fraud_score_hourly` | Fraud | Tier 1 | Criterion 2 | Fraud Ops Lead | _(fill in)_ |
| EX-003 | `inventory_sync_intraday` | Inventory | Tier 1 | Criterion 1 — feeds storefront availability | Supply Chain Director | _(fill in)_ |
| EX-004 | `finance_gl_reconciliation` | Finance | Tier 1 | Criterion 3 — SOX close deadline | Controller | _(fill in)_ |
| EX-005 | `marketing_campaign_attribution` | Marketing | Tier 2 | Manual workaround exists (delayed dashboard refresh) | Marketing Analytics Lead | _(fill in)_ |
| EX-006 | `weekly_merchandising_adhoc_report` | Merchandising | Tier 3 | Standard analytics, no time-sensitivity confirmed | — | _(fill in)_ |
| EX-007 | `legacy_vendor_feed_2019` | Unknown | Tier 4 | No consumer identified in any interview | — | _(fill in)_ |

Rows above are illustrative examples — every job in
[`06-job-inventory.md`](06-job-inventory.md) must receive a tier assignment
here before [`14-job-migration/`](../../14-job-migration/README.md) wave
planning begins.

## Dispute resolution

If a job owner and a business interview disagree on tier (e.g., engineering
believes a job is Tier 3, the business owner insists Tier 1), the dispute is
resolved by the Migration Program Lead applying the objective criteria
above literally — if no criterion is met, the job is not Tier 1, regardless
of how strongly it's asserted to be important. Escalate to the RACI
Accountable party (Program Lead) rather than defaulting to the more
conservative tier, which causes tier inflation over time.

## Common Mistakes

- **Tier inflation** — defaulting everything uncertain to Tier 1 "to be
  safe." This defeats the purpose of tiering and collapses wave
  sequencing back into "migrate everything with maximum caution," which is
  not economically viable.
- **Assigning tiers without business confirmation** — engineering's guess
  at business impact is frequently wrong in both directions.

## Production Notes

Re-validate Tier 1/2 assignments against actual behavior during the last
peak trading event (Black Friday/Cyber Monday) if data exists — a job that
seems Tier 2 in steady state may function as Tier 1 during peak load.
