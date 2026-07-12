# Pain Points & Bottlenecks (Consolidated)

**Purpose:** Consolidate every pain point and bottleneck surfaced across
this folder and the Discovery interviews into a single, prioritized list —
the explicit "things the migration must actually fix" register, so
[`04-target-architecture/`](../04-target-architecture/README.md) is
designed against real, evidenced problems rather than generic cloud-
migration talking points.
**Owner:** Migration Program Lead, synthesized from Platform Engineering
findings.
**Inputs:** Every document in this folder, plus
[`01-discovery/questions/02-platform-team.md`](../01-discovery/questions/02-platform-team.md)
and
[`01-discovery/questions/07-operations.md`](../01-discovery/questions/07-operations.md)
findings.
**Outputs:** A checklist [`04-target-architecture/`](../04-target-architecture/README.md)
must explicitly address, item by item, not just implicitly improve on.
**Validation method:** Every pain point listed must cite the specific
evidence (which document/section/interview) that established it — no
pain point should be included solely because "everyone knows that's a
problem."

---

## Consolidated pain points

| # | Pain Point | Evidence Source | Severity | Root Cause | Must Target Architecture Explicitly Address? |
|---|---|---|---|---|---|
| 1 | Fixed hardware capacity forces over-provisioning for peak, under-utilization off-peak | [`08-resource-utilization-report.md`](08-resource-utilization-report.md) | High | Physical hardware procurement cycle | Yes — autoscaling design in [`12-cluster-design/`](../12-cluster-design/README.md) |
| 2 | Single, non-HA NameNode / Metastore (if confirmed) is a single point of failure | [`01-hadoop-cluster-assessment.md`](01-hadoop-cluster-assessment.md), [`04-hive-environment-assessment.md`](04-hive-environment-assessment.md) | High | Historical architecture decision, never revisited | Yes — managed services (GCS, Dataproc Metastore) resolve this by design |
| 3 | Queue contention causes job queueing delays during nightly batch window | [`02-yarn-resource-assessment.md`](02-yarn-resource-assessment.md) | Medium-High | Shared cluster capacity model | Yes — ephemeral per-workload clusters in [`12-cluster-design/`](../12-cluster-design/README.md) |
| 4 | Hardware nearing/past end-of-life on a subset of worker nodes | [`01-hadoop-cluster-assessment.md`](01-hadoop-cluster-assessment.md) | Medium | Deferred hardware refresh | Indirectly — migration itself resolves this by removing dependency on the hardware |
| 5 | Legacy text/CSV-format Hive tables cause excess storage and query cost | [`04-hive-environment-assessment.md`](04-hive-environment-assessment.md) | Medium | Historical data ingestion patterns never modernized | Yes — format conversion scoped in [`06-data-migration/`](../06-data-migration/README.md) |
| 6 | No tested DR/backup restore process | [`01-discovery/inventories/05-disaster-recovery-rpo-rto.md`](../01-discovery/inventories/05-disaster-recovery-rpo-rto.md) | High | Backup existed but was never validated end-to-end | Yes — explicit DR design and testing in [`04-target-architecture/`](../04-target-architecture/README.md) |
| 7 | Manual, undocumented operational interventions required for some jobs | [`01-discovery/questions/02-platform-team.md`](../01-discovery/questions/02-platform-team.md) | Medium | Accumulated technical debt, tribal knowledge | Yes — idempotency/retry redesign in [`07-spark-migration/`](../07-spark-migration/README.md) |
| 8 | Client-mode Spark jobs carry edge-node-local dependencies | [`03-spark-environment-assessment.md`](03-spark-environment-assessment.md) | Medium | Historical submission pattern, never standardized | Yes — standardized Dataproc submission pattern in [`07-spark-migration/`](../07-spark-migration/README.md) |
| 9 | Gap between documented security policy and actual enforced configuration | [`06-security-configuration-assessment.md`](06-security-configuration-assessment.md) | High | Policy drift over time, no regular audit cadence | Yes — deliberate IAM design in [`10-security/`](../10-security/README.md), not a 1:1 port |
| 10 | Skilled on-prem Hadoop administration talent is scarce/aging in the market | [`00-project-overview/01-executive-summary.md`](../00-project-overview/01-executive-summary.md) | Medium (strategic, not immediate) | Broader market trend | Indirectly — managed services reduce this dependency |

_(Illustrative rows — populate exhaustively from actual findings across
this folder before this document is considered complete; every "High"
severity item must have an explicit corresponding design decision recorded
in [`04-target-architecture/`](../04-target-architecture/README.md) or
[`decisions/`](../decisions/README.md) as an ADR.)_

## Severity definitions

| Severity | Definition |
|---|---|
| **High** | Actively causes business impact today (incidents, missed SLAs, security exposure) or blocks a required migration outcome if uncorrected |
| **Medium** | Causes operational friction or inefficiency but has workarounds in current use |
| **Low** | Cosmetic or convenience-level improvement opportunity |

## How this feeds the rest of the program

Every "High" severity pain point becomes a **named success criterion** for
[`04-target-architecture/`](../04-target-architecture/README.md) — the
target design document must explicitly state, per pain point, how the new
architecture resolves it (or explicitly accept it as an out-of-scope
residual risk, with sign-off). This traceability is what separates a real
migration engineering document from a generic "move to the cloud" pitch
deck.

## Common Mistakes

- Listing generic cloud-migration talking points ("cloud is more scalable")
  instead of evidenced, specific pain points from this platform's actual
  data.
- Failing to close the loop — recording pain points here but never
  checking, at [`04-target-architecture/`](../04-target-architecture/README.md)
  review, whether each one was actually addressed.

## Production Notes

Pain points affecting Tier 1 business functions (pricing, fraud, finance,
inventory) should be explicitly called out to the Executive Sponsor and
affected Business Owners as part of the [`00-project-overview/01-executive-summary.md`](../00-project-overview/01-executive-summary.md)
narrative — these are the pain points that most directly justify the
program's cost and effort to a non-technical audience.
