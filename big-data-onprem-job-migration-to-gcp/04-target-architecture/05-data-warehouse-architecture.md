# Data Warehouse Architecture — BigQuery vs. Dataproc-Hive Decision Framework

**Purpose:** Provide an explicit, repeatable, per-table decision framework
for whether a given Hive table's target on GCP is BigQuery or a
Dataproc-managed Hive Metastore pattern — replacing the blanket-rule
anti-pattern warned against in
[`04-target-architecture/README.md`](README.md).
**Owner:** Data Engineering + Platform Engineering, applied to every table
in [`01-discovery/inventories/09-hive-inventory.md`](../01-discovery/inventories/09-hive-inventory.md).

---

## Decision framework

For each table, score against the following criteria:

| Criterion | Favors BigQuery | Favors Dataproc-managed Hive |
|---|---|---|
| Primary consumer | BI tools, analysts, ad-hoc SQL | Spark jobs, internal pipeline staging |
| Query pattern | Aggregation-heavy, ad-hoc, benefits from BigQuery's columnar engine and serverless scaling | High-mutation, frequently overwritten/appended by Spark jobs mid-pipeline |
| Data freshness need | Near-real-time available for query immediately after load | Intermediate/staging data, not meant for direct external query |
| Governance/access control need | Column/row-level security via BigQuery's native policy tags, fine-grained audit | Standard IAM-scoped access sufficient |
| Table size and growth | Very large (multi-TB/PB), benefits from BigQuery's fully managed scaling | Any size, especially where Spark-native read/write performance matters more than SQL query latency |
| Cost profile fit | Query-based billing suits sporadic/ad-hoc access patterns | Storage-based (GCS) cost suits high-volume, programmatically-accessed pipeline data |

## Applying the framework — worked examples

| Table (from Hive inventory) | Primary Consumer | Query Pattern | Decision | Rationale |
|---|---|---|---|---|
| `pricing.daily_price_snapshot` | BI dashboards + `pricing_nightly_batch` | High-frequency aggregation queries from BI | **BigQuery** | High BI/analyst usage, benefits from BigQuery's query performance and governance |
| `fraud.txn_feature_scores` | `fraud_score_hourly` (Spark) + fraud service | High-frequency read/write, low-latency needed by Spark job | **BigQuery** (with BI Engine or materialized views for the service-facing read path) or **Dataproc-Hive** if sub-second Spark-native read latency is required — validate in [`17-performance/`](../17-performance/README.md) before finalizing |
| `finance.gl_reconciliation_monthly` | Finance analysts, `finance_gl_reconciliation` job | Low-frequency, high-governance | **BigQuery** — column-level security fits SOX governance requirement |
| Internal Spark staging tables (intermediate pipeline state, never queried directly by humans) | Spark jobs only | High-mutation, pipeline-internal | **Dataproc-managed Hive** (or plain GCS/Parquet without a Hive table at all, if no SQL access is ever needed) |
| `legacy.vendor_feed_2019_raw` | None confirmed | N/A — retirement candidate | **Neither** — resolve via [`01-discovery/inventories/06-job-inventory.md`](../01-discovery/inventories/06-job-inventory.md) retirement process before this decision is needed |

## Hybrid pattern: BigQuery external tables over GCS

For tables that are large, infrequently queried, but occasionally need SQL
access, consider **BigQuery external tables** reading directly from GCS
Parquet files — avoiding a full load into BigQuery-managed storage while
still enabling ad-hoc SQL access. This is a middle-ground option worth
evaluating per table, not just the two "pure" options above.

## Migrating UDFs into this framework

Per
[`01-discovery/inventories/09-hive-inventory.md`](../01-discovery/inventories/09-hive-inventory.md)
UDF inventory: any table moving to BigQuery whose queries depend on a
custom Hive UDF requires that UDF to be reimplemented as a BigQuery SQL UDF
or a BigQuery remote function — this is scoped explicitly in
[`08-hive-migration/`](../08-hive-migration/README.md) and must be
completed *before* the dependent table's migration wave, not concurrently.

## Recording the decision

Every table's decision from this framework must be recorded back into
[`01-discovery/inventories/09-hive-inventory.md`](../01-discovery/inventories/09-hive-inventory.md)'s
"Target on GCP" column — this framework document defines *how* the
decision is made; the inventory is *where* each actual decision is
recorded, keeping a single source of truth.

## Common Mistakes

- Applying "BigQuery for everything" because it's simpler to explain to
  stakeholders — this creates unnecessary cost for high-volume,
  pipeline-internal staging data that never needs SQL query access.
- Applying "Dataproc-Hive for everything" to minimize migration effort —
  this forfeits BigQuery's governance, performance, and serverless scaling
  benefits for exactly the BI/analyst-facing tables that would benefit
  most, undermining part of the business case in
  [`00-project-overview/01-executive-summary.md`](../00-project-overview/01-executive-summary.md).

## Production Notes

For Tier 1 tables where the decision is close (e.g., `fraud.txn_feature_scores`
above), do not finalize the decision on paper alone — build a small
proof-of-concept for both options and measure actual latency/cost in
[`17-performance/`](../17-performance/README.md) before committing, since
the cost of being wrong on a Tier 1 table's warehouse target is high.
