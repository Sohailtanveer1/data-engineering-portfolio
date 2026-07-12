# Aggregation Validation

**Purpose:** Validate business-meaningful aggregates (sums, averages,
counts by dimension) match between source and target — catching a class of
error (a subtle transformation bug that shifts values without changing row
count) that count/checksum validation alone won't always surface as
clearly.
**Owner:** Data Engineering.

---

## Standard aggregation checks

| Check | Example (Pricing Domain) |
|---|---|
| Sum of a key numeric column | `SUM(final_price)` matches between source and target within tolerance |
| Average | `AVG(discount_percent)` matches |
| Min/Max | `MIN(base_price)`, `MAX(base_price)` match — catches outlier handling differences |
| Count by dimension | `COUNT(*) GROUP BY pricing_zone` matches per zone, not just in total (catches a join/filter bug that shifts totals between categories while preserving the grand total) |
| Distinct count | `COUNT(DISTINCT sku)` matches |

## Why group-by aggregation matters beyond a single total

A transformation bug that misassigns records between categories (e.g., a
zone-mapping join bug) can leave the **grand total** row count and sum
unchanged while being completely wrong at the group level — this is
precisely the kind of error that count/checksum-only validation misses
and group-by aggregation validation catches directly.

## Business-meaningful aggregation examples per domain

| Domain | Aggregation Check |
|---|---|
| Pricing | Total revenue-equivalent (`SUM(final_price * quantity)`) by category, matching source |
| Fraud | Count of transactions flagged above the review threshold, matching source |
| Finance | Sum of GL entries by account code, matching to the cent (zero tolerance) |
| Inventory | Total on-hand quantity by warehouse, matching source |

These are derived directly from the business logic confirmed in
[`01-discovery/questions/05-business.md`](../01-discovery/questions/05-business.md)
— not generic aggregations, but the specific numbers the business actually
cares about and would notice being wrong.

## Tolerance guidance

| Data Type | Default Tolerance |
|---|---|
| Financial/monetary values | 0 (exact match to the cent) — never loosened without Finance sign-off |
| Percentages/ratios | Small tolerance (e.g., 0.01%) for floating-point representation |
| Counts | 0 (exact match) |

## Common Mistakes

- Validating only grand totals and skipping group-by validation, missing
  category-shifting bugs.
- Applying a loose tolerance to financial aggregation checks by default,
  rather than requiring explicit Finance sign-off for any tolerance beyond
  exact match.

## Production Notes

For finance and pricing domains specifically, aggregation validation
checks should be reviewed and approved by the actual Business Owner (not
just Data Engineering) to confirm the chosen aggregations are the ones
that would actually reveal a business-meaningful error — engineering's
intuition about which aggregates matter can differ from the business's.
