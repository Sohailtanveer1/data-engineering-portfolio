# Preemptible & Spot VM Strategy

**Purpose:** Balance cost savings (a major driver of the business case in
[`00-project-overview/01-executive-summary.md`](../00-project-overview/01-executive-summary.md))
against the SLA risk of workload interruption, per job tier.
**Owner:** Platform Engineering, coordinated with
[`19-cost-optimization/`](../19-cost-optimization/README.md).

---

## Preemptible/spot usage policy by tier

| Job Tier | Preemptible/Spot Worker Usage | Rationale |
|---|---|---|
| Tier 1 (business-critical) | Secondary workers only, capped at 40-50% of max cluster capacity, primary workers always on-demand | Bounds the risk of a mass-preemption event derailing an SLA-critical run, while still capturing meaningful cost savings |
| Tier 2 | Secondary workers, up to 60-70% of max capacity | More cost-aggressive given lower SLA sensitivity |
| Tier 3 | Secondary workers, up to 80%+ of max capacity, or fully preemptible where the job easily tolerates a restart | Maximizes cost savings for the lowest-risk workloads |
| Streaming (persistent, e.g., fraud scoring) | No preemptible workers | Preemption mid-stream risks state loss/reprocessing complexity disproportionate to the cost savings for a small, always-on cluster |

## How Dataproc handles preemption gracefully

Dataproc's primary/secondary worker model means preemptible ("secondary")
workers can be lost without taking down the cluster's core YARN/HDFS
services (which run on primary workers) — a preempted secondary worker's
tasks are automatically retried on remaining capacity. This is why
capping, not eliminating, preemptible usage for Tier 1 jobs is a
reasonable risk/cost balance, rather than an all-or-nothing choice.

## Handling task-level retry cost from preemption

Even with graceful handling, a preempted worker's in-flight tasks must be
re-executed — for shuffle-heavy jobs, this can be more costly than the
raw compute time lost. Combine the preemptible cap above with the
`graceful_decommission_timeout` tuning from
[`03-autoscaling-policies.md`](03-autoscaling-policies.md) to minimize
this cost, and validate the actual observed impact in
[`17-performance/`](../17-performance/README.md) before finalizing the
cap percentage for each Tier 1 job family.

## Spot VMs vs. classic preemptible VMs

Prefer **Spot VMs** (the current generation) over classic preemptible VMs
where supported by the target Dataproc image — Spot VMs have no fixed
24-hour maximum lifetime (unlike classic preemptible), better suiting
longer-running batch jobs without an arbitrary interruption point
unrelated to actual capacity needs.

## Common Mistakes

- Applying a single preemptible percentage uniformly across all tiers
  instead of the tier-differentiated policy above, either over-exposing
  Tier 1 to interruption risk or under-capturing available cost savings
  for Tier 3.
- Using preemptible/spot workers for the streaming fraud-scoring cluster
  to save cost, without accounting for the state-recovery complexity a
  mid-stream preemption introduces.

## Production Notes

Track actual preemption frequency and its measured impact on job duration
for every Tier 1 job family during
[`14-job-migration/`](../14-job-migration/README.md) parallel-run
validation — adjust the preemptible cap based on real observed impact,
not just the theoretical policy, before full production reliance.
