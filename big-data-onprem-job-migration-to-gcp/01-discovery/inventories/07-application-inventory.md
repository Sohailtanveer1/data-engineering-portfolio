# Application Inventory

**Purpose:** Catalog the applications/systems that sit around the Hadoop
platform — as data sources, data sinks, or operational tooling — so
[`04-target-architecture/`](../../04-target-architecture/README.md) and
[`11-network/`](../../11-network/README.md) know every integration point
that must be preserved through migration.
**Owner:** Migration Program Lead, populated with Platform Engineering and
Business/Developer interviews.
**Inputs:** [`questions/06-developers.md`](../questions/06-developers.md),
[`questions/04-networking-team.md`](../questions/04-networking-team.md),
architecture diagrams if they exist (often outdated — verify).
**Outputs:** Feeds [`02-dependency-analysis/`](../../02-dependency-analysis/README.md)
external-dependency mapping and [`11-network/`](../../11-network/README.md)
connectivity design.

---

## Application inventory table

| Application | Type | Relationship to Hadoop Platform | Integration Method | Data Direction | Owning Team | Stays On-Prem or Migrates? |
|---|---|---|---|---|---|---|
| Order Management System (OMS) | Core transactional system | Source of order data | Sqoop/JDBC batch extract | OMS → Hadoop | Ecommerce Platform Team | Stays on-prem (out of migration scope per charter) |
| Point of Sale (POS) | Core transactional system | Source of in-store sales data | Batch file drop (SFTP) | POS → Hadoop | Retail Systems Team | Stays on-prem |
| Payment Gateway | Third-party/internal | Source of payment transaction metadata | Batch extract (via intermediary system, not direct) | Gateway → Hadoop | Payments Team | Stays on-prem |
| Warehouse Management System (WMS) | Core operational system | Source of inventory/fulfillment data | Kafka topic + batch reconciliation | WMS → Hadoop | Supply Chain Systems Team | Stays on-prem |
| Marketing Automation Platform | SaaS | Consumer of campaign attribution output | REST API push | Hadoop → Platform | Marketing Data Eng | Stays external (SaaS); integration re-pointed to GCP |
| BI Tool (Tableau/Looker/Power BI) | Analytics tool | Consumer of Hive tables/views | JDBC/ODBC | Hadoop → BI Tool | BI/Analytics Team | Reconnected to BigQuery/Dataproc post-migration |
| Vendor/Partner data exchange | External | Bi-directional data exchange | SFTP | Bi-directional | Data Engineering | Integration re-pointed; partner may need to be notified of endpoint change |
| Fraud detection scoring service | Internal service | Consumer of fraud feature output | REST API / message queue | Hadoop → Service | Fraud Engineering | Stays on-prem or migrates separately — confirm ownership and scope boundary explicitly |

_(Illustrative rows only — populate exhaustively from interviews and actual
integration configuration; do not assume this list is complete without a
follow-up integration architecture review with each owning team.)_

## Why "stays on-prem" applications still matter to this migration

Every application marked "stays on-prem" above still needs a **persistent
connectivity path** to the GCP platform per
[`11-network/`](../../11-network/README.md), and its integration method
(Sqoop, SFTP, Kafka, REST) needs an explicit GCP-side redesign per
[`06-data-migration/`](../../06-data-migration/README.md) — "not in
scope for migration" does not mean "not in scope for the network/
integration design."

## Common Mistakes

- Treating this as an IT asset inventory exercise rather than an
  integration-point exercise — the goal is not to list every application
  in the company, only those that exchange data with the Hadoop platform.
- Missing SaaS/third-party integrations because they don't show up in
  internal network diagrams — these are exactly the ones prone to breaking
  silently if endpoint URLs/credentials change during migration.

## Production Notes

For payment-adjacent and fraud-adjacent integrations specifically,
loop in Security early (see
[`questions/03-security-team.md`](../questions/03-security-team.md)) — these
integration points often carry compliance scope that constrains how they
can be redesigned.
