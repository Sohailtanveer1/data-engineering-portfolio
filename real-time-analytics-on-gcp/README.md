# Real-Time Supply Chain Order & Inventory Analytics Platform

## Business Context

Warehouses across the supply chain network continuously emit **Order**,
**Inventory**, **Shipment**, **Return**, and **Supplier** events. Today these
events land in disconnected systems and are only visible to analysts hours
later via batch reports. That delay means stockouts, overselling, and
delayed shipments are discovered after they've already cost the business
money.

This platform ingests those events in real time, validates and enriches
them, and serves curated, trustworthy metrics to operations and finance
within seconds of an event occurring — not hours.

## Architecture

```
Warehouses (event sources)
      │
      ▼
Kafka (local, Dockerized)          <- durable local ingestion buffer
      │
      ▼
Google Pub/Sub                      <- cloud-native, scalable ingestion
      │
      ▼
Dataflow (Apache Beam, streaming)   <- validation, enrichment, dedup, windowing
      │
      ▼
BigQuery — Medallion Architecture
   Bronze (raw)  →  Silver (cleaned/conformed)  →  Gold (business marts)
      │
      ▼
Looker Studio                       <- dashboards for ops/finance
```

Supporting infrastructure (Terraform-managed, environment-isolated across
`dev` / `uat` / `prod`): VPC, firewall rules, IAM & service accounts, Secret
Manager, Cloud Storage, Cloud Logging/Monitoring.

## Repository Layout

| Path | Purpose |
|---|---|
| `kafka/` | Local Kafka producers, consumers, Docker Compose stack, Avro/JSON schemas |
| `dataflow/` | Apache Beam streaming pipeline (Pub/Sub → BigQuery) |
| `bigquery/` | Medallion schemas (bronze/silver/gold) and SQL |
| `infra/terraform/` | Reusable Terraform modules + per-environment configs |
| `docs/` | Architecture, diagrams, API docs, business docs, guides |
| `.github/workflows/` | CI/CD: lint, test, `terraform plan`, deploy |
| `tests/` | Unit, integration, and pipeline tests |
| `looker/` | Looker Studio dashboard definitions/notes |
| `scripts/` | Operational scripts (local bootstrap, replay, backfill) |

## Project Status

✅ **Repo complete** — Kafka ingestion, Pub/Sub bridge, Terraform-managed
GCP infrastructure (dev/uat/prod), the Beam/Dataflow streaming pipeline,
BigQuery Medallion layers, CI/CD, and full documentation are all built. 23
tests pass. See [docs/lessons-learned.md](docs/lessons-learned.md) for the
running log of decisions and known gaps (flagged explicitly, not hidden).

**Not yet done:** actually deploying this to a live GCP project — that's
a manual step you run yourself, following [RUNBOOK.md](RUNBOOK.md).

## Getting Started

- **To deploy this yourself, step by step:** [RUNBOOK.md](RUNBOOK.md) —
  exact commands, in order, with a verification checkpoint after each one.
- **To understand why it's built this way:** [docs/setup-guide.md](docs/setup-guide.md)
  (the map) and [docs/architecture/architecture-overview.md](docs/architecture/architecture-overview.md)
  (every data engineering concept explained with business value + interview framing).

## Documentation Index

| Doc | Covers |
|---|---|
| [RUNBOOK.md](RUNBOOK.md) | Step-by-step deployment to your own GCP project |
| [docs/setup-guide.md](docs/setup-guide.md) | High-level order of operations and prerequisites |
| [docs/architecture/architecture-overview.md](docs/architecture/architecture-overview.md) | Every DE concept (idempotency, dedup, watermarking, exactly-once, ...) with business value and interview framing |
| [docs/architecture/kafka-topic-design.md](docs/architecture/kafka-topic-design.md) | Topic naming, partition keys, replication rationale |
| [docs/diagrams/sequence/](docs/diagrams/sequence/) | Mermaid sequence diagrams: happy path, DLQ path, replay |
| [docs/diagrams/network/](docs/diagrams/network/) | Network topology and firewall reasoning |
| [docs/api/README.md](docs/api/README.md) | Event schema contracts + Gold view contracts |
| [docs/business/README.md](docs/business/README.md) | Business context, stakeholders, why real-time |
| [docs/security-guide.md](docs/security-guide.md) | Every IAM grant, explained |
| [docs/monitoring-guide.md](docs/monitoring-guide.md) | Alert-by-alert on-call runbook |
| [docs/troubleshooting-guide.md](docs/troubleshooting-guide.md) | DLQ triage, pipeline errors, local dev setup issues |
| [docs/testing-guide.md](docs/testing-guide.md) | What's tested, how to run it, what's intentionally not automated |
| [docs/cost-optimization.md](docs/cost-optimization.md) | Every cost lever, with reasoning |
| [docs/interview-questions.md](docs/interview-questions.md) | Curated Q&A across the whole platform |
| [docs/lessons-learned.md](docs/lessons-learned.md) | Real decisions, real problems hit, honest gaps |
| [infra/terraform/README.md](infra/terraform/README.md) | Terraform module layout and design rationale |
| [looker/dashboard-spec.md](looker/dashboard-spec.md) | Exact Looker Studio dashboard spec to build from |
