# Migration Playbook — Build Progress Tracker

This file tracks the build status of this repository itself (not the
customer migration). It exists because this playbook is built incrementally,
one folder at a time, to production depth — never generated in bulk as
placeholder text.

**Legend:** ✅ Complete &nbsp;|&nbsp; 🚧 Pending (skeleton only) &nbsp;|&nbsp; ⏳ In progress

| # | Folder | Status | Last Updated | Notes |
|---|---|---|---|---|
| — | `README.md` (root) | ✅ Complete | 2026-07-12 | Master index |
| — | `MIGRATION-PROGRESS.md` | ✅ Complete | 2026-07-12 | This file |
| 00 | `00-project-overview/` | ✅ Complete | 2026-07-12 | Charter, RACI, timeline, glossary |
| 01 | `01-discovery/` | ✅ Complete | 2026-07-12 | 8 stakeholder question sets + 12 inventories |
| 02 | `02-dependency-analysis/` | ✅ Complete | 2026-07-12 | 9 methodology docs + 3 reusable templates |
| 03 | `03-current-environment/` | ✅ Complete | 2026-07-12 | Hadoop/YARN/Spark/Hive/storage/security/config baseline + utilization + pain points |
| 04 | `04-target-architecture/` | ✅ Complete | 2026-07-12 | Full system design, landing zone, compute/storage/warehouse/orchestration/security/network architecture, ADR log, pain-point traceability |
| 05 | `05-storage-migration/` | ✅ Complete | 2026-07-12 | Strategy, DistCp/STS runbooks, incremental sync, checksum validation, permissions mapping, rollback, execution checklist |
| 06 | `06-data-migration/` | ✅ Complete | 2026-07-12 | Historical/incremental/CDC/snapshot strategy, partitioning, format standard, reconciliation, execution runbook |
| 07 | `07-spark-migration/` | ✅ Complete | 2026-07-12 | Restructuring, version/API migration, Dataproc submission, packaging, config/secrets, logging/retry, idempotency, OOP patterns, testing strategy + 6 working code examples (syntax-verified) |
| 08 | `08-hive-migration/` | ✅ Complete | 2026-07-12 | Metastore strategy, external/managed tables, partitions, statistics, views, UDF migration, execution runbook |
| 09 | `09-composer-migration/` | ✅ Complete | 2026-07-12 | Oozie/cron conversion, dynamic DAG generation, best practices, monitoring/retry/alerts, config mgmt + 2 working DAG examples (syntax-verified) |
| 10 | `10-security/` | ✅ Complete | 2026-07-12 | IAM design, service accounts, Secret Manager, KMS/encryption, audit logging, break-glass, key rotation, review checklist |
| 11 | `11-network/` | ✅ Complete | 2026-07-12 | VPC/subnet design, firewall, private connectivity/NAT, DNS, VPN/Interconnect decision, routes/peering, execution checklist |
| 12 | `12-cluster-design/` | ✅ Complete | 2026-07-12 | Topology decision, node sizing, autoscaling, preemptible strategy, HA design, governance, init actions/custom images |
| 13 | `13-infrastructure/` | ✅ Complete | 2026-07-12 | Folder structure, backend/state, naming standards, module usage guide, environment promotion, state ops, execution checklist |
| 14 | `14-job-migration/` | ✅ Complete | 2026-07-12 | Priority matrix, wave planning, migration tracker, parallel-run strategy, execution steps, rollback, deployment checklist |
| 15 | `15-testing/` | ✅ Complete | 2026-07-12 | Test strategy matrix, regression, smoke, end-to-end, recovery, chaos, negative, performance testing process |
| 16 | `16-data-validation/` | ✅ Complete | 2026-07-12 | Validation framework architecture, count/checksum, aggregation, business rules, duplicate/null detection, reporting, continuous production validation |
| 17 | `17-performance/` | ✅ Complete | 2026-07-12 | Shuffle, partition, broadcast joins, AQE, caching, skew handling, executor sizing/dynamic allocation, Dataproc-specific tuning |
| 18 | `18-monitoring/` | ✅ Complete | 2026-07-12 | Logging architecture, dashboards, alerting, error reporting, SLA dashboards, on-call/escalation |
| 19 | `19-cost-optimization/` | ✅ Complete | 2026-07-12 | Cost baseline/attribution, compute/storage optimization, scheduling, rightsizing review, budget monitoring |
| 20 | `20-uat/` | 🚧 Pending | 2026-07-12 | |
| 21 | `21-cutover/` | 🚧 Pending | 2026-07-12 | |
| 22 | `22-hypercare/` | 🚧 Pending | 2026-07-12 | |
| — | `architecture/` | 🚧 Pending | 2026-07-12 | |
| — | `diagrams/` | 🚧 Pending | 2026-07-12 | |
| — | `terraform/` | 🚧 Pending | 2026-07-12 | |
| — | `scripts/` | 🚧 Pending | 2026-07-12 | |
| — | `templates/` | 🚧 Pending | 2026-07-12 | |
| — | `sample-config/` | 🚧 Pending | 2026-07-12 | |
| — | `sample-code/` | 🚧 Pending | 2026-07-12 | |
| — | `ci-cd/` | 🚧 Pending | 2026-07-12 | |
| — | `documentation/` | 🚧 Pending | 2026-07-12 | |
| — | `checklists/` | 🚧 Pending | 2026-07-12 | |
| — | `runbooks/` | 🚧 Pending | 2026-07-12 | |
| — | `decisions/` | 🚧 Pending | 2026-07-12 | |
| — | `logs/` | 🚧 Pending | 2026-07-12 | |

## Build order

Numbered phase folders (`01` → `22`) are built in order, since later phases
reference deliverables from earlier ones. Cross-cutting folders are built
opportunistically as the numbered phase that most depends on them is built
(e.g., `terraform/` gets its first real modules alongside `13-infrastructure/`,
`ci-cd/` alongside `07-spark-migration/` and `13-infrastructure/`).

## How to resume this build

If you are picking this repository build back up in a new session: read this
file, find the first `🚧 Pending` numbered phase, and build it completely
(all files, no placeholders) before moving to the next. Update this table's
status and date when a folder is completed.
