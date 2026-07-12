# 12 — Dataproc Cluster Design

## Purpose

Turn the compute pattern decisions from
[`04-target-architecture/03-compute-architecture.md`](../04-target-architecture/03-compute-architecture.md)
into concrete, sized, per-job-family Dataproc cluster configurations —
using the actual resource footprint data from
[`01-discovery/inventories/08-spark-inventory.md`](../01-discovery/inventories/08-spark-inventory.md)
and utilization data from
[`03-current-environment/08-resource-utilization-report.md`](../03-current-environment/08-resource-utilization-report.md),
not guesswork.

## Owner

**Platform Engineering**, with resource sizing reviewed against
[`19-cost-optimization/`](../19-cost-optimization/README.md).

## Inputs

- Compute architecture decisions from
  [`04-target-architecture/03-compute-architecture.md`](../04-target-architecture/03-compute-architecture.md).
- Per-job resource footprint from
  [`01-discovery/inventories/08-spark-inventory.md`](../01-discovery/inventories/08-spark-inventory.md).
- Peak utilization data from
  [`03-current-environment/08-resource-utilization-report.md`](../03-current-environment/08-resource-utilization-report.md).

## Outputs

- A per-job-family cluster configuration template (machine types, worker
  counts, autoscaling policy) ready for Terraform implementation.
- Documented preemptible/spot usage strategy.
- HA design for any persistent clusters.

## Prerequisites

[`04-target-architecture/`](../04-target-architecture/README.md) gated;
[`11-network/`](../11-network/README.md) substantially complete (clusters
need a VPC/subnet to launch into).

## Deliverables

1. Cluster topology decision per job family.
2. Node sizing and machine type selection.
3. Autoscaling policy design.
4. Preemptible/spot VM strategy.
5. High availability design for persistent clusters.
6. Cluster policies and governance (who can create what).
7. Initialization actions and custom image strategy.

## Risks

Under-sizing Tier 1 job clusters based on average (not peak) resource
footprint data is the primary risk in this folder — mitigated by the
explicit peak-data requirement throughout.

## Rollback

Cluster configurations are Terraform-managed and version-controlled — a
misconfigured cluster template is corrected via a new Terraform apply, not
a manual fix, and takes effect on the next cluster creation (ephemeral
clusters recreate on every job run, so a fix propagates immediately to the
next run).

## Validation

Every Tier 1 job family's cluster configuration must be load-tested
against peak-equivalent volume in
[`17-performance/`](../17-performance/README.md) before being relied upon
in production.

## Best Practices

Default to ephemeral, autoscaled clusters per
[`04-target-architecture/03-compute-architecture.md`](../04-target-architecture/03-compute-architecture.md);
reserve persistent clusters for the specific, justified exceptions (
streaming, very short/frequent jobs, interactive workloads) documented
there.

## Lessons Learned

Copying on-prem YARN queue capacity allocations directly into Dataproc
cluster sizing produces poorly-fitted clusters, since on-prem sizing
reflects shared-queue contention compromises, not a job's actual
standalone resource need.

## Common Mistakes

- Sizing every job family's cluster identically "for simplicity" instead
  of using each family's actual measured resource footprint.
- Using 100% preemptible/spot workers for a Tier 1 job with a hard SLA,
  risking a mid-run large-scale preemption event derailing a
  business-critical pipeline.

## Production Notes

Tier 1 job clusters should use a mixed on-demand/preemptible worker
strategy (see
[`04-preemptible-and-spot-strategy.md`](04-preemptible-and-spot-strategy.md)),
never 100% preemptible, to bound the risk of a mass-preemption event
threatening SLA.

---

## Folder structure

```
12-cluster-design/
├── README.md                                            This file
├── 01-cluster-topology-decision.md                       Ephemeral/persistent per job family
├── 02-node-sizing-and-machine-types.md                    Master/worker sizing
├── 03-autoscaling-policies.md                             Autoscaling policy design
├── 04-preemptible-and-spot-strategy.md                    Cost/risk-balanced preemptible usage
├── 05-high-availability-design.md                          HA for persistent clusters
├── 06-cluster-policies-and-governance.md                   Who can create what, and how
└── 07-initialization-actions-and-custom-images.md          Cluster-level dependency installation
```
