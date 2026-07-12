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
| 05 | `05-storage-migration/` | 🚧 Pending | 2026-07-12 | |
| 06 | `06-data-migration/` | 🚧 Pending | 2026-07-12 | |
| 07 | `07-spark-migration/` | 🚧 Pending | 2026-07-12 | |
| 08 | `08-hive-migration/` | 🚧 Pending | 2026-07-12 | |
| 09 | `09-composer-migration/` | 🚧 Pending | 2026-07-12 | |
| 10 | `10-security/` | 🚧 Pending | 2026-07-12 | |
| 11 | `11-network/` | 🚧 Pending | 2026-07-12 | |
| 12 | `12-cluster-design/` | 🚧 Pending | 2026-07-12 | |
| 13 | `13-infrastructure/` | 🚧 Pending | 2026-07-12 | |
| 14 | `14-job-migration/` | 🚧 Pending | 2026-07-12 | |
| 15 | `15-testing/` | 🚧 Pending | 2026-07-12 | |
| 16 | `16-data-validation/` | 🚧 Pending | 2026-07-12 | |
| 17 | `17-performance/` | 🚧 Pending | 2026-07-12 | |
| 18 | `18-monitoring/` | 🚧 Pending | 2026-07-12 | |
| 19 | `19-cost-optimization/` | 🚧 Pending | 2026-07-12 | |
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
