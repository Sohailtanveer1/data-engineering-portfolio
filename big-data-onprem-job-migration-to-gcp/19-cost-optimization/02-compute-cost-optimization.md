# Compute Cost Optimization

**Purpose:** Apply cost discipline to the Dataproc compute layer —
autoscaling, cluster lifecycle, and preemptible/spot usage — building
directly on the design decisions in
[`12-cluster-design/`](../12-cluster-design/README.md) rather than
introducing new patterns.
**Owner:** Platform Engineering.

---

## Ephemeral clusters as the primary cost lever

The single largest cost optimization in this migration is architectural,
not tactical: the ephemeral-cluster-by-default pattern from
[`04-target-architecture/03-compute-architecture.md`](../04-target-architecture/03-compute-architecture.md)
eliminates idle capacity cost entirely for the majority of workloads — a
job that runs for 2 hours costs for 2 hours, not for 24/7 cluster
uptime as the on-prem fixed-capacity model effectively did.

## Preemptible/spot usage

Per
[`12-cluster-design/04-preemptible-and-spot-strategy.md`](../12-cluster-design/04-preemptible-and-spot-strategy.md),
tier-differentiated preemptible/spot usage captures significant savings
(preemptible/spot VMs are typically 60-91% cheaper than on-demand) while
bounding SLA risk for Tier 1 workloads. Track actual realized savings per
job family:

| Job Family | % Secondary (Preemptible) Workers | Estimated Savings vs. All On-Demand |
|---|---|---|
| `pricing_nightly_batch` (Tier 1) | 40% cap | ~25-30% blended compute savings |
| `weekly_merchandising_adhoc_report` (Tier 3) | 80%+ | ~50-60% blended compute savings |

## Cluster lifecycle discipline

Every mechanism preventing orphaned/idle clusters (per
[`12-cluster-design/06-cluster-policies-and-governance.md`](../12-cluster-design/06-cluster-policies-and-governance.md))
is a direct cost control — track the **orphaned cluster incident rate**
as a cost-relevant metric, not just an operational one, and treat any
occurrence as worth investigating for both operational and cost reasons.

## Right-sizing based on real utilization

Revisit cluster sizing (per
[`12-cluster-design/02-node-sizing-and-machine-types.md`](../12-cluster-design/02-node-sizing-and-machine-types.md))
using **actual observed GCP utilization** once jobs have run in
production for a meaningful period — initial sizing was based on on-prem
data as the best available proxy; real GCP execution data is a better
long-term sizing input, captured via
[`05-rightsizing-review-process.md`](05-rightsizing-review-process.md).

## Committed use discounts (for persistent workloads)

For the small set of persistent clusters (streaming, interactive, per
[`12-cluster-design/01-cluster-topology-decision.md`](../12-cluster-design/01-cluster-topology-decision.md)),
evaluate Committed Use Discounts once usage patterns are stable and
predictable (typically after several months of production operation, not
during the volatile migration period itself) — a 1 or 3-year commitment on
volatile, still-changing infrastructure risks locking in the wrong shape.

## Common Mistakes

- Applying Committed Use Discounts too early, before usage patterns are
  stable, risking a mismatched commitment as the platform's real shape
  becomes clearer post-migration.
- Not tracking realized preemptible/spot savings against the estimate,
  missing the chance to catch a job family where preemption frequency is
  higher than expected, eroding the theoretical savings with retry cost.

## Production Notes

Reassess preemptible/spot caps for every job family after its first full
peak trading season — actual observed preemption behavior and cost
savings during real peak load is the most reliable input for whether the
current caps are well-calibrated.
