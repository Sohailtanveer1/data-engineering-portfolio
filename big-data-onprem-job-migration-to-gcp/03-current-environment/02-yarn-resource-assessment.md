# YARN Resource Assessment

**Purpose:** Document how compute capacity is currently allocated and
contended for across the cluster — memory, CPU, executor patterns, and
queue structure — as the direct input to autoscaling policy and cluster
sizing decisions in [`12-cluster-design/`](../12-cluster-design/README.md).
**Owner:** Platform Engineering.
**Inputs:** `yarn-site.xml`, `capacity-scheduler.xml` or
`fair-scheduler.xml`, YARN Resource Manager UI/REST API, YARN
Timeline Server history (if retained).
**Outputs:** Feeds [`12-cluster-design/`](../12-cluster-design/README.md)
autoscaling policy design and queue-to-ephemeral-cluster mapping decisions.

---

## Cluster-wide resource capacity

| Metric | Value |
|---|---|
| Total YARN memory capacity | _(fill in)_ |
| Total YARN vCore capacity | _(fill in)_ |
| Scheduler type | _(Capacity Scheduler / Fair Scheduler)_ |
| `yarn.nodemanager.resource.memory-mb` (per node) | _(fill in)_ |
| `yarn.nodemanager.resource.cpu-vcores` (per node) | _(fill in)_ |
| `yarn.scheduler.maximum-allocation-mb` | _(fill in)_ |
| Container overcommit/oversubscription enabled? | _(yes/no, details)_ |

## Queue configuration

| Queue Name | Capacity % (or weight) | Max Capacity % | Owning Team(s) | Typical Utilization | Contention Observed? |
|---|---|---|---|---|---|
| `default` | | | | | |
| `pricing` | | | | | |
| `fraud` | | | | | |
| `finance` | | | | | |
| `adhoc` | | | | | |

_(Populate with actual queue configuration from
`capacity-scheduler.xml`/`fair-scheduler.xml`; illustrative queue names
shown above.)_

## Executor / application resource patterns

Aggregate from the per-job data already captured in
[`01-discovery/inventories/08-spark-inventory.md`](../01-discovery/inventories/08-spark-inventory.md):

| Metric | P50 across all Spark jobs | P95 across all Spark jobs | Max observed |
|---|---|---|---|
| Executors per job | | | |
| Executor memory | | | |
| Executor cores | | | |
| Driver memory | | | |
| Total job duration | | | |

## Contention and queueing behavior

| Question | Finding |
|---|---|
| Do jobs regularly wait in YARN `ACCEPTED` state before running? | |
| Which queue(s) see the most contention, and at what times? | |
| Is preemption enabled, and does it fire regularly? | |
| Are there jobs that fail specifically due to resource unavailability (not application errors)? | |

This directly answers whether the current platform's capacity model is a
genuine constraint the business feels (supports the executive summary's
capacity-cap argument) or a well-managed steady state — be honest here,
since it shapes how the target architecture's autoscaling story is framed
to the sponsor.

## What changes fundamentally on Dataproc

Unlike a single shared YARN cluster with queues mediating contention
between teams, the default target pattern in
[`12-cluster-design/`](../12-cluster-design/README.md) is **ephemeral,
per-job or per-workload-family Dataproc clusters** — which removes queue
contention as a concept entirely for many workloads, replacing it with
per-job resource allocation and cluster-level autoscaling. Where a
persistent shared cluster is still the right pattern (e.g., for
interactive/ad-hoc workloads), queue-equivalent behavior is achieved via
Dataproc autoscaling policies, documented explicitly in
[`12-cluster-design/`](../12-cluster-design/README.md) — this document's
queue data is the sizing input, not something to be replicated 1:1.

## Common Mistakes

- Sizing target Dataproc clusters off `yarn.nodemanager.resource.memory-mb`
  capacity figures without accounting for actual observed utilization —
  provisioned capacity and used capacity are often very different numbers,
  and cost-efficient GCP sizing should target actual usage patterns, not
  on-prem's static capacity ceiling.
- Ignoring queue-level access control (which teams can submit to which
  queue) — this is a security/governance pattern that needs an explicit
  GCP-native equivalent (IAM-scoped service accounts, potentially separate
  Dataproc clusters per team) in
  [`10-security/`](../10-security/README.md) and
  [`12-cluster-design/`](../12-cluster-design/README.md).

## Production Notes

Capture queue utilization specifically during the last peak trading event
if metrics retention allows — this is the single most important data point
for correctly sizing autoscaling policies for Tier 1 workloads on Dataproc.
