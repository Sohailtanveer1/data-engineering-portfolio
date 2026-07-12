# Business Rule Validation

**Purpose:** Encode the specific business rules confirmed during Discovery
as executable, automated checks — the validation category most directly
tied to *correctness*, as opposed to *completeness* (counts/checksums) or
*consistency* (aggregations).
**Owner:** Data Engineering, rules confirmed by Business Owners.

---

## Sourcing business rules

Every business rule validated here traces back to a specific, confirmed
statement from
[`01-discovery/questions/05-business.md`](../01-discovery/questions/05-business.md)
or
[`01-discovery/questions/06-developers.md`](../01-discovery/questions/06-developers.md)
— never an assumption engineering makes independently about "what seems
reasonable."

## Example business rule checks

| Rule | Source | Validation Query Pattern |
|---|---|---|
| Discount percent never exceeds the configured cap | Merchandising, confirmed in Discovery | `SELECT COUNT(*) FROM pricing.daily_price_snapshot WHERE discount_percent > 40` — must return 0 |
| Fraud score is always between 0 and 100 | Fraud Engineering | `SELECT COUNT(*) FROM fraud.txn_feature_scores WHERE score < 0 OR score > 100` — must return 0 |
| Every order has a non-null fulfillment status once 24 hours have passed | Supply Chain | `SELECT COUNT(*) FROM inventory.orders WHERE order_age_hours > 24 AND fulfillment_status IS NULL` — must return 0 |
| GL entries always balance (debits = credits) per journal entry | Finance, SOX-relevant | `SELECT journal_id, SUM(debit) - SUM(credit) AS imbalance FROM finance.gl_entries GROUP BY journal_id HAVING imbalance != 0` — must return zero rows |

## Why this check type is unique

Count, checksum, and aggregation checks are all effectively "does the
target match the source" — they don't catch a bug that exists **in both**
the source and the newly-migrated logic identically, nor do they validate
against an independent standard of correctness. Business rule checks are
different: they validate against the business's own stated invariants,
independent of what the source system happens to currently produce —
useful both for migration validation and for ongoing production data
quality monitoring (a business rule violation in production, regardless of
migration, is worth knowing about).

## Building the business rule catalog

Maintain a single catalog (a version-controlled document or table)
mapping every confirmed business rule to its corresponding validation
check — reviewed and updated whenever
[`01-discovery/questions/05-business.md`](../01-discovery/questions/05-business.md)
findings are updated, and whenever a new business rule surfaces during
ongoing operation (e.g., discovered via a UAT finding in
[`20-uat/`](../20-uat/README.md)).

## Handling rule violations

| Context | Handling |
|---|---|
| Found during parallel-run validation | Investigate — is this a migration bug, or does the on-prem source also violate this rule (revealing the rule was aspirational, not actually enforced)? Resolve explicitly, don't assume |
| Found in ongoing production (post-cutover) | Treated as a data quality incident, per [`22-hypercare/`](../22-hypercare/README.md) or standard operational incident process thereafter |

## Common Mistakes

- Writing business rule checks from engineering's own assumptions instead
  of confirmed statements from the actual business interviews — an
  incorrect assumed rule produces false-positive validation failures that
  erode trust in the framework.
- Discovering that the on-prem source itself violates a "confirmed" rule
  and treating this as a migration validation framework bug rather than a
  pre-existing data quality issue worth surfacing to the business
  regardless of the migration.

## Production Notes

For Tier 1 domains, build the business rule catalog collaboratively with
the Business Owner in a working session, not via a one-way document
review — rules are often easier to state correctly in conversation than
to extract from a static interview transcript alone.
