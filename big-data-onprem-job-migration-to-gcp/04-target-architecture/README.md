# 04 — Target Architecture

## Purpose

This is the pivot point of the entire program: everything before this
folder is about understanding what exists ([`01-discovery/`](../01-discovery/README.md),
[`02-dependency-analysis/`](../02-dependency-analysis/README.md),
[`03-current-environment/`](../03-current-environment/README.md)); everything
after it is about building and executing against the design defined here.
This folder is where the on-prem pain points documented in
[`03-current-environment/09-pain-points-and-bottlenecks.md`](../03-current-environment/09-pain-points-and-bottlenecks.md)
either get explicitly resolved by a design decision, or explicitly and
consciously deferred — never silently carried forward.

## Owner

**Migration Program Lead**, designed jointly with **Platform Engineering**,
**Cloud/DevOps**, **Security**, and **Network Engineering** leads (per the
RACI in
[`00-project-overview/03-raci-matrix.md`](../00-project-overview/03-raci-matrix.md)).

## Inputs

- Completed [`01-discovery/`](../01-discovery/README.md),
  [`02-dependency-analysis/`](../02-dependency-analysis/README.md), and
  [`03-current-environment/`](../03-current-environment/README.md).
- GCP organizational context: does an existing GCP organization, folder
  structure, or landing zone already exist (per assumption A1 in
  [`00-project-overview/06-assumptions-and-constraints.md`](../00-project-overview/06-assumptions-and-constraints.md))?

## Outputs

- A complete, reviewed, and approved target architecture that every
  subsequent phase (`05-` through `13-`) implements against.
- An explicit decision record, per pain point, showing how the target
  design resolves it.

## Prerequisites

Phases 02 and 03 gated (see
[`00-project-overview/04-timeline-and-phases.md`](../00-project-overview/04-timeline-and-phases.md)).

## Deliverables

1. Target architecture overview with full system diagram.
2. Landing zone and GCP project structure design.
3. Compute architecture (Dataproc patterns).
4. Storage architecture (GCS bucket/structure design).
5. Data warehouse architecture (BigQuery vs. Dataproc-Hive decision
   framework, applied per table).
6. Orchestration architecture (Cloud Composer placement and pattern).
7. Security architecture overview (detailed in
   [`10-security/`](../10-security/README.md)).
8. Network architecture overview (detailed in
   [`11-network/`](../11-network/README.md)).
9. Architecture decision log.
10. Explicit pain-point-to-resolution traceability matrix.

## Risks

- **Over-engineering for a hypothetical future** instead of this
  platform's actual, evidenced requirements — every design choice here
  should be traceable to a Discovery finding or a current-environment pain
  point, not a generic "cloud best practice" applied without justification.
- **Under-specifying the target**, leaving too much to be decided ad-hoc
  during execution phases, which reintroduces the same configuration drift
  problem the current platform suffers from (see
  [`03-current-environment/06-security-configuration-assessment.md`](../03-current-environment/06-security-configuration-assessment.md)).

## Rollback

N/A — this is a design phase; nothing is deployed yet. (Rollback becomes
relevant once [`13-infrastructure/`](../13-infrastructure/README.md) starts
applying this design via Terraform.)

## Validation

This folder is gated (per
[`00-project-overview/04-timeline-and-phases.md`](../00-project-overview/04-timeline-and-phases.md))
only when Platform Engineering, Security, and Network leads have all
formally reviewed and approved the design — not merely "no objections
raised."

## Best Practices

Design per-workload, not platform-wide uniformly. Not every Hive table
belongs in BigQuery; not every Spark job belongs on the same cluster
topology. The decision frameworks in this folder ([`05-data-warehouse-architecture.md`](05-data-warehouse-architecture.md)
in particular) exist specifically to make these per-workload decisions
consistent and defensible rather than ad-hoc.

## Lessons Learned

Migrations that pick "BigQuery for everything" or "lift-and-shift Hive to
Dataproc for everything" as a blanket rule, without a per-workload decision
framework, either overpay for BigQuery on workloads that don't need it, or
fail to capture BigQuery's real benefits where they'd matter most.

## Common Mistakes

- Designing the target architecture without explicit reference to the pain
  points catalogued in
  [`03-current-environment/09-pain-points-and-bottlenecks.md`](../03-current-environment/09-pain-points-and-bottlenecks.md)
  — see [`10-pain-point-traceability.md`](10-pain-point-traceability.md),
  which exists to force this connection explicitly.
- Designing security and network as an afterthought bolted onto a compute/
  storage-first design — see [`07-security-architecture-overview.md`](07-security-architecture-overview.md)
  and [`08-network-architecture-overview.md`](08-network-architecture-overview.md),
  which are first-class parts of this design, not appendices.

## Production Notes

Every architecture decision that affects a Tier 1 business function
(pricing, fraud, finance, inventory — per
[`01-discovery/inventories/02-business-critical-jobs.md`](../01-discovery/inventories/02-business-critical-jobs.md))
must be explicitly called out and separately reviewed with that function's
Business Owner before this folder is considered gated.

---

## Folder structure

```
04-target-architecture/
├── README.md                                    This file
├── 01-target-architecture-overview.md            Full system diagram, GCP service mapping
├── 02-landing-zone-and-project-structure.md      Org/folder/project hierarchy, environments
├── 03-compute-architecture.md                    Dataproc patterns (ephemeral/persistent/serverless)
├── 04-storage-architecture.md                    GCS bucket structure and storage classes
├── 05-data-warehouse-architecture.md              BigQuery vs. Dataproc-Hive decision framework
├── 06-orchestration-architecture.md               Cloud Composer placement and pattern
├── 07-security-architecture-overview.md           High-level IAM/KMS/Secret Manager (detail in 10-security/)
├── 08-network-architecture-overview.md            High-level connectivity (detail in 11-network/)
├── 09-architecture-decision-log.md                Key decisions made in this phase (full ADRs in decisions/)
└── 10-pain-point-traceability.md                  Explicit pain-point-to-resolution mapping
```
