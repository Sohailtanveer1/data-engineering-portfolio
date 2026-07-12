# 03 — Current Environment Analysis

## Purpose

[`01-discovery/`](../01-discovery/README.md) captured *what* runs on the
platform and *who* depends on it. This phase captures *how the platform
itself is built and configured* — the technical baseline that
[`04-target-architecture/`](../04-target-architecture/README.md) sizes and
designs against. Without an accurate current-state technical baseline,
target Dataproc cluster sizing in
[`12-cluster-design/`](../12-cluster-design/README.md) is guesswork, not
engineering.

## Owner

**Platform Engineering**, coordinated by the Migration Program Lead. This
folder runs largely in parallel with
[`01-discovery/`](../01-discovery/README.md) — see the phase gate table in
[`00-project-overview/04-timeline-and-phases.md`](../00-project-overview/04-timeline-and-phases.md).

## Inputs

- Direct read access to cluster configuration files
  (`core-site.xml`, `hdfs-site.xml`, `yarn-site.xml`, `hive-site.xml`,
  `spark-defaults.conf`, `capacity-scheduler.xml`/`fair-scheduler.xml`).
- Access to cluster monitoring/metrics history (Ambari/Cloudera Manager,
  Ganglia, or equivalent) covering at least 90 days, ideally including one
  peak trading event.
- Findings from [`01-discovery/questions/02-platform-team.md`](../01-discovery/questions/02-platform-team.md).

## Outputs

- A complete, version-accurate technical baseline of the current platform.
- A documented, evidence-based set of pain points and bottlenecks that
  [`04-target-architecture/`](../04-target-architecture/README.md) and
  [`12-cluster-design/`](../12-cluster-design/README.md) must explicitly
  address (not silently reproduce on GCP).

## Prerequisites

Phase 01 gated or substantially in progress (this phase can run in
parallel, but final sign-off waits on Discovery's platform-team interview
being complete, since several findings here should be cross-validated
against that interview).

## Deliverables

1. Hadoop cluster assessment (topology, node counts, hardware).
2. YARN resource assessment (memory, CPU, executors, queues).
3. Spark environment assessment (version, configuration defaults).
4. Hive environment assessment (Metastore backing store, HiveServer2
   configuration).
5. Storage & network assessment (disk layout, intra-cluster network).
6. Security configuration assessment (as-deployed Kerberos/Ranger state).
7. Configuration baseline (every relevant config file, version-pinned).
8. Resource utilization report (with peak-period data).
9. Pain points & bottlenecks (consolidated, evidence-based).

## Risks

- **Documentation drift.** The single biggest risk in this phase is
  trusting a wiki page or architecture diagram instead of pulling live
  configuration — every document in this folder must cite where its data
  came from (a specific config file, a specific metrics dashboard query),
  not "known to the team."
- **Sampling bias in utilization data.** Utilization pulled only from a
  quiet period will understate true peak requirements — see the peak-load
  requirement in
  [`08-resource-utilization-report.md`](08-resource-utilization-report.md).

## Rollback

N/A — this phase is read-only assessment.

## Validation

Every configuration value and version number recorded in this folder must
be traceable to a specific source file or command output, referenced
inline. A reviewer should be able to re-run the cited command and get the
same answer.

## Best Practices

Pull configuration and metrics data programmatically wherever possible
(scripted export of XML config files, scripted metrics API queries) rather
than manual transcription — this also produces a reusable baseline snapshot
that can be diffed later if the on-prem environment changes during the
program.

## Lessons Learned

Cluster sizing decisions made from "what we think we're using" rather than
measured utilization data are the single most common cause of
under-provisioned (causing performance regressions) or wildly over-
provisioned (blowing the cost budget) target Dataproc clusters.

## Common Mistakes

- Assessing the cluster during a known-quiet period and calling it
  representative.
- Documenting the *intended* Kerberos/Ranger security configuration from
  policy documents instead of the *actual, currently enforced*
  configuration, which frequently drifts from policy over time.

## Production Notes

Prioritize gathering utilization data that spans at least one full
month-end close and, if at all possible, a slice of the last peak trading
event (Black Friday/Cyber Monday) — steady-state Tuesday metrics will not
reveal the true peak resource envelope
[`12-cluster-design/`](../12-cluster-design/README.md) must be designed
for.

---

## Folder structure

```
03-current-environment/
├── README.md                                  This file
├── 01-hadoop-cluster-assessment.md             Topology, node counts, hardware, HDFS
├── 02-yarn-resource-assessment.md              Memory, CPU, executors, queues
├── 03-spark-environment-assessment.md          Spark version and runtime configuration
├── 04-hive-environment-assessment.md           Hive Metastore and HiveServer2 configuration
├── 05-storage-and-network-assessment.md        Disk layout, intra-cluster network
├── 06-security-configuration-assessment.md     As-deployed Kerberos/Ranger/LDAP state
├── 07-configuration-baseline.md                Full config file inventory, version-pinned
├── 08-resource-utilization-report.md           Utilization metrics, including peak period
└── 09-pain-points-and-bottlenecks.md           Consolidated, evidence-based findings
```
