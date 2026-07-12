# Acceptance Criteria

**Purpose:** Define, in advance and in writing, exactly what the Business
Owner will check during UAT and what "acceptable" means — removing
ambiguity that could otherwise let UAT slip into either a rubber-stamp
formality or an open-ended, never-satisfied review.
**Owner:** Business Owner (defines, with Migration Program Lead
facilitation), agreed before UAT begins.

---

## Acceptance criteria template (per job/domain)

| Criterion Category | Specific Criterion | How Verified |
|---|---|---|
| Data correctness | Output matches on-prem for [specific business scenario, e.g., "last month's pricing calculations"] | Business Owner or delegate directly queries/reviews the migrated output |
| Data completeness | No missing records for [specific known edge case, e.g., "products added mid-month"] | Spot-check against a known reference |
| Timeliness | Data available by [business-expected time, per [`01-discovery/inventories/01-sla-inventory.md`](../01-discovery/inventories/01-sla-inventory.md)] | Observed during the UAT window |
| Usability | Reports/dashboards built on the migrated data render correctly and perform acceptably | Business Owner directly interacts with their actual tooling |
| Known business rules | [Specific confirmed rule, e.g., "discount never exceeds 40%"] holds in migrated output | Business Owner spot-checks or reviews validation report from [`16-data-validation/04-business-rule-validation.md`](../16-data-validation/04-business-rule-validation.md) |

## Example — Pricing domain acceptance criteria

1. Daily price snapshot for the last 30 days matches on-prem values within
   $0.01 for a sample of 100 randomly selected SKUs, verified directly by
   the Merchandising Director.
2. The Merchandising team's existing Tableau dashboard, repointed to the
   migrated BigQuery table, renders without error and matches previously
   known-correct figures for the last closed month.
3. No discount value in the migrated table exceeds the confirmed 40% cap.
4. Data is available by 3:00 AM as per the business-expected SLA.

## Setting criteria before UAT starts

Acceptance criteria are drafted by the Migration Program Lead (informed
by
[`01-discovery/questions/05-business.md`](../01-discovery/questions/05-business.md)
findings) and reviewed/finalized with the Business Owner **before** the
job enters the UAT window — never defined retroactively based on what
happened to be checked.

## Common Mistakes

- Criteria too vague to be actionable ("data looks right") — every
  criterion should be specific enough that pass/fail is unambiguous.
- Criteria set so narrow they miss a real issue a broader, more
  representative check would have caught — balance specificity with
  representative coverage of how the Business Owner actually uses the
  data.

## Production Notes

For Tier 1 domains, review draft acceptance criteria with the Business
Owner at least 2 weeks before the planned UAT window — this gives them
time to think through what actually matters to them, rather than
approving criteria reactively under time pressure.
