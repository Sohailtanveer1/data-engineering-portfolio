# Assumptions & Constraints

**Purpose:** Make explicit what this program is assuming to be true (so
that if an assumption turns out false, we know exactly which downstream
decisions need to be revisited) and what hard constraints bound our design
choices.
**Owner:** Migration Program Lead, validated by Platform Eng, Security, and
Network leads.
**Inputs:** Charter, early conversations with platform/security/network
teams (formalized in [`01-discovery/`](../01-discovery/README.md)).
**Outputs:** A log that every architecture decision in
[`04-target-architecture/`](../04-target-architecture/README.md) and
[`documentation/decisions/`](../decisions/README.md) can be traced back to.
**Validation:** Each assumption below must be confirmed or corrected during
[`01-discovery/`](../01-discovery/README.md); this document is updated the
moment an assumption is proven false.

---

## Assumptions

> An assumption is something we are proceeding *as if* true, without having
> fully verified it yet. Every assumption here must be explicitly verified
> during Discovery (`01-discovery/`) and either confirmed or struck through
> and corrected.

| # | Assumption | Why it matters if wrong | Verify in |
|---|---|---|---|
| A1 | The company has a landing zone / GCP organization already provisioned, or will provision one before Phase 04 | Target architecture and Terraform structure both assume an existing org/folder/project hierarchy | `04-target-architecture/`, `13-infrastructure/` |
| A2 | Business-critical jobs are a minority of total job count (typically 10–20% in comparable ecommerce estates) | Drives wave sequencing and risk budget — if most jobs are business-critical, the wave plan and freeze-window strategy both need to change | `01-discovery/`, `14-job-migration/` |
| A3 | Historical data beyond the compliance retention window does not need bit-for-bit migration, only compliant archival | Affects `06-data-migration/` scope and cost significantly | `01-discovery/` (retention & compliance section) |
| A4 | Existing Spark jobs are on a Spark version with a supported upgrade path to a Dataproc-supported Spark version | If jobs are on a very old Spark/Scala version, `07-spark-migration/` scope grows substantially (major version upgrade, not just re-platforming) | `03-current-environment/` |
| A5 | Network connectivity between on-prem and GCP (VPN or Interconnect) can be provisioned within the Foundation phase timeline | Parallel-run validation (`15-testing/`, `16-data-validation/`) depends on on-prem and GCP being able to reach shared reference data/systems during the transition | `11-network/` |
| A6 | The business can tolerate the defined freeze windows without requiring the migration to extend indefinitely around them | If freeze windows cover the majority of the calendar, program duration must be renegotiated | `02-migration-charter.md` |
| A7 | Kafka and/or Sqoop may or may not be present — the platform description mentions them as conditional | If present, they add scope requiring their own migration design; confirmed inventory determines this | `01-discovery/` |

## Constraints

> A constraint is a hard boundary we do not get to choose — imposed by
> compliance, existing contracts, technical reality, or business decision.
> Unlike assumptions, constraints are not something Discovery will
> "resolve" — they are inputs we design around.

| # | Constraint | Source | Impact |
|---|---|---|---|
| C1 | No business-critical cutover during change-freeze windows | Business/Exec Sponsor | Bounds `14-job-migration/` and `21-cutover/` scheduling |
| C2 | Data subject to regulatory retention (financial records, PII where applicable) must maintain chain-of-custody and auditability through migration | Compliance/Legal | Shapes `05-storage-migration/`, `06-data-migration/`, `10-security/` |
| C3 | Security model must pass formal security review before any production data moves to GCP | Security | Gates `04-target-architecture/` and `10-security/` before `05-storage-migration/` execution |
| C4 | Environments (dev/qa/stage/prod) must be fully isolated GCP projects, not shared-project namespaces | Security/Platform standard | Shapes `13-infrastructure/` Terraform and `ci-cd/` environment promotion design |
| C5 | All infrastructure must be provisioned via Terraform — no manual (ClickOps) production changes | Platform standard | Shapes `13-infrastructure/`, `ci-cd/` |
| C6 | Budget envelope is fixed per fiscal year; overruns require Exec Sponsor re-approval | Finance | Shapes `12-cluster-design/`, `19-cost-optimization/` |
| C7 | On-prem cluster must remain fully operational (undegraded) for any job not yet migrated, for the full duration of the program | Business continuity | Prohibits any "borrow capacity from decommissioning cluster" shortcuts during migration |

## What changes if an assumption is proven false

This document is a living artifact. When Discovery invalidates an
assumption (e.g., A4 turns out false because jobs are on Spark 1.6 with
deprecated RDD-only APIs), the Program Lead:

1. Updates this document, striking the assumption and recording the actual
   finding.
2. Flags every downstream document that referenced the assumption (search
   this repository for the phase folders listed in the "Verify in" /
   "Impact" columns above).
3. Logs the change and its cascading impact in
   [`decisions/`](../decisions/README.md) as a new ADR if it changes
   architecture, or in [`documentation/`](../documentation/README.md) risk
   register if it changes risk posture.
