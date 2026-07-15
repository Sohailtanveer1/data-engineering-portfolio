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

🚧 **Phase 1 of N — Foundations.** See [docs/lessons-learned.md](docs/lessons-learned.md)
(created as we go) for a running log of decisions and the phase roadmap.

## Getting Started

See [docs/setup-guide.md](docs/setup-guide.md) (populated in a later phase).
