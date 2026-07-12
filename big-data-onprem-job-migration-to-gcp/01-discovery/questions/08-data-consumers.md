# Discovery Questions — Data Consumers (Analysts, BI, Downstream Teams)

**Purpose:** Data consumers are frequently the last group consulted in a
migration and the first group to complain during UAT. This interview exists
to move that friction to Discovery, where it's cheap to address, instead of
[`20-uat/`](../../20-uat/README.md), where it's expensive.
**Owner:** Migration Program Lead, conducted with BI/Analytics leads and
representative power users of downstream reporting.
**Audience:** Data analysts, BI developers, downstream data engineering
teams building on top of this platform's output.

---

## Questions

| # | Question | Why we ask it |
|---|---|---|
| 1 | Which specific Hive tables, views, or query patterns do you rely on directly (not through a curated report)? | Ad-hoc/direct table access is easy to miss in a technical inventory built only from scheduled job definitions — this surfaces it explicitly. |
| 2 | What tool do you connect with (Tableau, Looker, Power BI, direct JDBC/ODBC, notebook environment), and how is that connection currently configured? | Every connection method needs an explicit GCP-side equivalent (e.g., BigQuery JDBC driver, new connection strings) planned in [`04-target-architecture/`](../../04-target-architecture/README.md) — silent breakage here has high visibility. |
| 3 | Are there specific SQL features, functions, or Hive UDFs your queries depend on? | Directly feeds the UDF migration scope in [`08-hive-migration/`](../../08-hive-migration/README.md) — a missing UDF breaks every query using it. |
| 4 | What's your tolerance for a query/dashboard being temporarily unavailable or slower during migration? | Sets realistic expectations and informs whether a given table needs parallel availability (old + new) during transition, per [`06-data-migration/`](../../06-data-migration/README.md). |
| 5 | Do you have saved queries, scheduled exports, or automation built on top of this platform that isn't visible to the platform team? | This is the most common "shadow dependency" category — self-service BI users build things platform teams never see, and these are exactly what breaks silently. |
| 6 | Are there data freshness expectations for your reports that differ from the documented job SLA? | Reveals gaps between documented SLA and actual expectation — feeds [`01-sla-inventory.md`](../inventories/01-sla-inventory.md). |
| 7 | Have you ever gotten wrong numbers from this platform that were hard to detect? What happened? | Past silent-correctness incidents are a strong signal for where [`16-data-validation/`](../../16-data-validation/README.md) needs the most rigor. |
| 8 | Who would you contact today if a report looked wrong, and how confident are you they'd find the root cause? | Reveals whether current data lineage/observability is adequate — informs whether the new platform needs better lineage tooling (e.g., Dataplex) than exists today. |
| 9 | Are there compliance or audit requirements tied to specific reports you produce (e.g., financial statements, regulatory filings)? | These reports carry correctness and availability requirements that must be explicitly protected, echoing constraint C2 in the assumptions/constraints log. |
| 10 | If you could change one thing about how you access this data today, what would it be? | Cheap opportunity to fix a real pain point as part of the migration (e.g., faster query performance via BigQuery) without it being scope creep — captured as an optional enhancement, not a requirement. |

## Validation of answers

Where possible, pull actual query logs (Hive/Presto/Spark Thrift Server
history) to identify active consumers and query patterns independently of
self-reported usage — self-service users often underreport what they
actually query regularly.
