# End-to-End Data Flow Diagram

**Purpose:** Show how data actually moves through the platform, end to
end, across every zone and transformation stage — complementing the
system context diagram's system-level view with a data-lifecycle view.
**Owner:** Migration Program Lead / Data Engineering.

---

```mermaid
flowchart LR
    subgraph Sources["Sources"]
        S1["On-prem systems<br/>(OMS/POS/WMS/Payment)"]
        S2["Vendor/partner feeds"]
    end

    subgraph Ingest["Ingestion"]
        I1["Storage Transfer Service /<br/>Composer SFTP operator /<br/>Pub-Sub"]
    end

    subgraph Raw["Raw Zone (GCS)"]
        R1["Immutable, as-received<br/>per 04-target-architecture/04-storage-architecture.md"]
    end

    subgraph Transform["Transformation (Dataproc/Spark)"]
        T1["Business logic per<br/>07-spark-migration/"]
    end

    subgraph Curated["Curated Zone (GCS + BigQuery)"]
        C1["Cleaned, validated,<br/>business-ready"]
    end

    subgraph Validate["Validation (continuous)"]
        V1["16-data-validation/<br/>runs after every transform"]
    end

    subgraph Archive["Archive Zone"]
        A1["Past active-use window,<br/>within retention"]
    end

    subgraph Consume["Consumption"]
        CO1["BI Tools"]
        CO2["Analysts"]
        CO3["Downstream jobs"]
        CO4["Partner exports"]
    end

    S1 --> I1
    S2 --> I1
    I1 --> R1
    R1 --> T1
    T1 --> C1
    T1 -.validated by.-> V1
    C1 -.validated by.-> V1
    C1 --> CO1
    C1 --> CO2
    C1 --> CO3
    C1 --> CO4
    C1 -->|lifecycle policy, per<br/>19-cost-optimization/03-storage-cost-optimization.md| A1
```

## Where each stage is detailed

| Stage | Detailed In |
|---|---|
| Ingestion | [`05-storage-migration/`](../05-storage-migration/README.md), [`06-data-migration/`](../06-data-migration/README.md) |
| Raw/Curated/Archive zoning | [`04-target-architecture/04-storage-architecture.md`](../04-target-architecture/04-storage-architecture.md) |
| Transformation | [`07-spark-migration/`](../07-spark-migration/README.md) |
| Validation | [`16-data-validation/`](../16-data-validation/README.md) |
| Consumption patterns | [`01-discovery/questions/08-data-consumers.md`](../01-discovery/questions/08-data-consumers.md), [`04-target-architecture/05-data-warehouse-architecture.md`](../04-target-architecture/05-data-warehouse-architecture.md) |

## Common Mistakes

- Treating this as a per-job diagram — it's intentionally the aggregate,
  cross-domain flow; individual job dependency graphs live in
  [`02-dependency-analysis/templates/01-dependency-graph-template.md`](../02-dependency-analysis/templates/01-dependency-graph-template.md).

## Production Notes

Use this diagram in stakeholder communication (e.g., alongside
[`00-project-overview/01-executive-summary.md`](../00-project-overview/01-executive-summary.md))
when explaining the platform's shape to a non-engineering audience — it's
deliberately less detailed than the target architecture overview, making
it more approachable for that purpose.
