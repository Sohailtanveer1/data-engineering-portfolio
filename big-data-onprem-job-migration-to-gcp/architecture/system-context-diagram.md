# System Context Diagram

**Purpose:** The single "zoomed all the way out" view of this platform's
boundary — every system it exchanges data with, on-prem and external,
regardless of migration phase. Useful for onboarding (per
[`documentation/onboarding-guide.md`](../documentation/onboarding-guide.md))
and for any stakeholder conversation needing the full picture without
implementation detail.
**Owner:** Migration Program Lead.

---

```mermaid
flowchart TB
    subgraph OnPremRemaining["On-Prem (Remains, Out of Migration Scope)"]
        OMS["Order Management System"]
        POS["Point of Sale"]
        WMS["Warehouse Management System"]
        PAY["Payment Gateway"]
    end

    subgraph External["External Systems"]
        VENDOR["Vendor/Partner SFTP Feeds"]
        MKTG["Marketing Automation (SaaS)"]
    end

    subgraph Platform["Data Platform (This Migration's Scope)"]
        direction TB
        GCS["Cloud Storage<br/>(raw / curated / archive)"]
        DATAPROC["Dataproc<br/>(Spark processing)"]
        BQ["BigQuery"]
        COMPOSER["Cloud Composer<br/>(orchestration)"]
    end

    subgraph Consumers["Data Consumers"]
        BI["BI Tools<br/>(Tableau/Looker/Power BI)"]
        ANALYSTS["Analysts / Data Scientists"]
        FRAUDSVC["Fraud Scoring Service"]
    end

    OMS -->|orders, CDC| GCS
    POS -->|sales data| GCS
    WMS -->|inventory, Kafka/batch| GCS
    PAY -->|payment metadata| GCS
    VENDOR -->|SFTP| GCS

    GCS --> DATAPROC
    DATAPROC --> GCS
    GCS --> BQ

    COMPOSER -.orchestrates.-> DATAPROC
    COMPOSER -.orchestrates.-> GCS

    BQ --> BI
    BQ --> ANALYSTS
    BQ --> MKTG
    DATAPROC --> FRAUDSVC

    style Platform fill:#e8f0fe,stroke:#4285f4
```

## Boundary notes

- Everything inside the **Platform** box is what this migration builds —
  see [`04-target-architecture/01-target-architecture-overview.md`](../04-target-architecture/01-target-architecture-overview.md)
  for the detailed internal architecture.
- Everything in **On-Prem Remaining** stays exactly where it is per the
  charter's out-of-scope section
  ([`00-project-overview/02-migration-charter.md`](../00-project-overview/02-migration-charter.md))
  — this migration changes *how* the platform connects to them (per
  [`11-network/`](../11-network/README.md)), not the systems themselves.
- The **Fraud Scoring Service** is shown as a consumer since it's
  downstream of the `fraud_score_hourly` pipeline — confirm its own
  hosting location (on-prem or GCP) per
  [`01-discovery/inventories/07-application-inventory.md`](../01-discovery/inventories/07-application-inventory.md),
  since this affects whether it's "external" or part of the platform
  boundary itself.

## Keeping this current

Update this diagram whenever a new external system integration is added
or an existing one is decommissioned — it should always reflect the
platform's actual current external boundary, not just its state at
migration kickoff.
