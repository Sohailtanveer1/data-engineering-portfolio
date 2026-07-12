# Risk Register — Program-Level Summary

**Purpose:** Surface the risks most likely to affect timeline, budget, or
data integrity, at a glance, for anyone reading only this overview folder.
**Owner:** Migration Program Lead (co-owned per-risk as noted).
**Inputs:** Discovery findings, architecture reviews, past-migration lessons
learned.
**Outputs:** Feeds the full, actively-managed risk register in
[`documentation/`](../documentation/README.md), which tracks status,
mitigation actions, and owners over time. This document is a point-in-time
summary; the full register is the living artifact.
**Validation:** Reviewed at every phase gate (see
[`04-timeline-and-phases.md`](04-timeline-and-phases.md)).

---

## Top program-level risks

| # | Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|---|
| R1 | Undiscovered job/data dependencies cause a production incident post-cutover | High | High | Exhaustive dependency analysis (`02-dependency-analysis/`) before any wave is scheduled; parallel-run validation before full cutover | Program Lead / Platform Eng |
| R2 | Data correctness regression (silent) not caught before cutover | Medium | Critical | Mandatory reconciliation framework (`16-data-validation/`) with sign-off gate before any wave is marked complete | Data Eng |
| R3 | Cutover during or adjacent to peak trading causes revenue-impacting incident | Low (if freeze windows respected) | Critical | Hard freeze windows in charter; wave scheduling explicitly checked against trading calendar | Program Lead / Business Owner |
| R4 | Cost overrun from mis-sized Dataproc clusters or inefficient storage tiering | Medium | Medium | Cost baseline + continuous monitoring (`19-cost-optimization/`); cluster sizing reviewed against actual workload profile, not guessed | Cloud/DevOps |
| R5 | Security model gap vs. on-prem Kerberos/Ranger controls | Medium | Critical | Formal security review gate before production data migration (`10-security/`); least-privilege IAM design reviewed against current Ranger policies | Security |
| R6 | Spark/Hive version upgrade surfaces breaking API changes across many jobs simultaneously | High | Medium | Version compatibility assessment in `03-current-environment/`; pilot-job-first approach in `07-spark-migration/` before scaling to full wave | Platform Eng |
| R7 | Orchestration logic in Oozie/cron encodes undocumented business rules that don't survive translation to Composer | Medium | High | Explicit logic review per job during `09-composer-migration/`, not a mechanical XML-to-DAG conversion | Data Eng |
| R8 | Key personnel (on-prem Hadoop SMEs) leave mid-migration, taking undocumented knowledge with them | Medium | High | Discovery captures tribal knowledge explicitly (`01-discovery/`); documentation-first culture enforced from Phase 00 | Program Lead |
| R9 | Network connectivity (VPN/Interconnect) between on-prem and GCP is delayed by procurement/vendor lead times | Medium | Medium | Network design and provisioning request initiated early in Foundation phase, not deferred to Phase 11 | Network |
| R10 | Parallel-run costs (running both platforms simultaneously) exceed budget if wave timelines slip | Medium | Medium | Wave plan includes explicit parallel-run duration caps per job tier; tracked in `19-cost-optimization/` | Program Lead |

## Risk severity definitions

| Level | Definition |
|---|---|
| **Critical** | Directly threatens revenue, compliance, or customer trust; could halt the program |
| **High** | Causes significant rework, timeline slip of weeks, or a P1 production incident |
| **Medium** | Causes moderate rework or timeline slip of days |
| **Low** | Contained, recoverable within normal execution |

## Full risk register

The complete, actively-managed risk register — including per-risk status,
detection method, contingency trigger, and update history — lives in
[`documentation/`](../documentation/README.md) and is reviewed at every
phase gate defined in
[`04-timeline-and-phases.md`](04-timeline-and-phases.md). This summary is
refreshed from that source whenever a top-10 risk changes materially.
