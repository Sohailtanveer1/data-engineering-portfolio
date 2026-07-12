# Data Retention & Compliance Inventory

**Purpose:** Determine, per dataset, how long data must be kept, under
what compliance obligation, and in what form — this directly scopes
[`06-data-migration/`](../../06-data-migration/README.md) (what must be
migrated bit-for-bit vs. what can be compliantly archived) and
[`10-security/`](../../10-security/README.md) (encryption/access
requirements per classification).
**Owner:** Migration Program Lead, populated with Security/Compliance and
Legal input (see
[`questions/03-security-team.md`](../questions/03-security-team.md)).
**Inputs:** Current retention policy documents (if any exist), regulatory
requirements applicable to the business (PCI-DSS, SOX, GDPR/CCPA, industry-specific).
**Outputs:** Directly gates data migration scope and archival strategy.
**Validation method:** Legal/Compliance sign-off required on every retention
period below — do not rely on engineering's assumption of retention needs.

---

## Retention & compliance inventory

| Data Domain | Classification | Retention Requirement | Regulatory Basis | Current Storage Location | Migration Treatment |
|---|---|---|---|---|---|
| Customer PII (order/account records) | Restricted | 7 years post account closure (example — confirm actual) | GDPR/CCPA + internal policy | HDFS `/data/customer/` | Full migration to GCS with CMEK; access controls per `10-security/` |
| Payment transaction metadata (non-cardholder-data) | Restricted | 7 years | PCI-DSS adjacent, financial audit | HDFS `/data/payments/` | Full migration; confirm PCI scope boundary explicitly with Security before migration — do not assume out of PCI scope |
| Order/fulfillment history | Confidential | 3 years active, archive beyond | Internal policy, tax/audit | HDFS `/data/orders/` | Active window migrated to GCS Standard; older data to GCS Coldline/Archive per `19-cost-optimization/` |
| Financial GL / reconciliation data | Restricted | 7 years | SOX | HDFS `/data/finance/` | Full migration, immutable/WORM-equivalent storage class considered |
| Clickstream / web analytics | Internal | 13 months (example) | Internal policy, marketing use | HDFS `/data/clickstream/` | Migrate active window; evaluate aggregation before archival to reduce volume |
| Fraud model features/scores | Restricted | Per fraud team policy (confirm) | Internal + potential regulatory | HDFS `/data/fraud/` | Full migration, tightly scoped IAM |
| Vendor/partner feeds | Confidential | Per contract terms (confirm per partner) | Contractual | HDFS `/data/partners/` | Confirm per-partner retention individually — do not apply a blanket policy |

_(Rows above are illustrative — every data domain identified in
[`11-storage-inventory.md`](11-storage-inventory.md) must have a
corresponding row here, confirmed with Legal/Compliance, not assumed by
engineering.)_

## Compliance frameworks applicable to this platform

| Framework | Applies to | Key implication for migration |
|---|---|---|
| PCI-DSS | Any payment-adjacent data | May require specific GCP configuration (network segmentation, encryption, access logging) — confirm scope boundary explicitly with Security |
| SOX | Financial reporting data | Requires immutable audit trail and change control evidence through the migration itself |
| GDPR / CCPA (as applicable) | Customer PII | Data residency, right-to-erasure implications — confirm whether right-to-erasure requests must be honored against migrated/archived copies too |
| Industry-specific (if any) | Confirm during discovery | — |

_(Confirm which frameworks actually apply — do not assume all apply
equally to all ecommerce companies; this varies by market and product
category.)_

## Common Mistakes

- Assuming "keep everything forever" is the safe default — this increases
  both migration cost and compliance risk (data you don't need to keep is
  data you don't need to protect, migrate, or produce under legal
  discovery).
- Migrating data without confirming its actual classification first —
  under-protecting restricted data is worse than the cost of asking first.
- Forgetting that retention requirements apply to migrated **backups** and
  **archives** too, not just the primary copy.

## Production Notes

Confirm explicitly with Legal whether any data subject to a **legal hold**
exists today — legal holds override normal retention/deletion policy and
must be preserved through migration regardless of the standard retention
period listed above.
