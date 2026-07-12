# Autoscaling Policies

**Purpose:** Configure Dataproc autoscaling for persistent clusters and
appropriately-sized initial/max bounds for ephemeral clusters, directly
resolving pain point #1 (fixed capacity) and #3 (queue contention) from
[`03-current-environment/09-pain-points-and-bottlenecks.md`](../03-current-environment/09-pain-points-and-bottlenecks.md).
**Owner:** Platform Engineering.

---

## Autoscaling policy template

```hcl
# Terraform excerpt — see 13-infrastructure/
resource "google_dataproc_autoscaling_policy" "pricing_family_policy" {
  policy_id = "pricing-family-autoscaling"
  location  = var.region

  worker_config {
    min_instances = 4
    max_instances = 12
    weight        = 1
  }

  secondary_worker_config {
    min_instances = 0
    max_instances = 20     # preemptible/spot burst capacity, see 04-preemptible-and-spot-strategy.md
    weight        = 1
  }

  basic_algorithm {
    yarn_config {
      graceful_decommission_timeout = "3600s"
      scale_up_factor                = 0.5
      scale_down_factor              = 0.5
      scale_up_min_worker_fraction   = 0.0
      scale_down_min_worker_fraction = 0.0
    }
    cooldown_period = "120s"
  }
}
```

## Bounds per job family

| Job Family | Min Workers | Max Workers | Secondary (Preemptible) Max |
|---|---|---|---|
| `pricing_nightly_batch` | 4 (ephemeral cluster's initial size) | 12 | 20 |
| `fraud_score_hourly` (persistent, streaming) | 4 | 8 | 0 — no preemptible for streaming state stability, see [`04-preemptible-and-spot-strategy.md`](04-preemptible-and-spot-strategy.md) |
| `inventory_sync_intraday` | 3 | 6 | 10 |

Bounds are set from the resource footprint data in
[`02-node-sizing-and-machine-types.md`](02-node-sizing-and-machine-types.md),
with the max bound sized to comfortably cover peak-trading-equivalent load
identified in
[`03-current-environment/08-resource-utilization-report.md`](../03-current-environment/08-resource-utilization-report.md),
not just typical steady-state peak.

## Scale-up/scale-down tuning

- **`graceful_decommission_timeout`** is set generously (e.g., 1 hour) for
  jobs with long-running shuffle-dependent tasks, avoiding data loss from
  premature worker removal mid-task — validate the right value per job
  family in [`17-performance/`](../17-performance/README.md).
- **`cooldown_period`** prevents thrashing (rapid scale up/down cycling)
  — tuned per job family's actual load variability pattern, not left at
  an untested default for Tier 1 workloads.

## Why ephemeral clusters still benefit from autoscaling

Even though ephemeral clusters are sized per job, a job's own load can
vary within a single run (e.g., a highly skewed join stage needing more
capacity than the initial read stage) — autoscaling within a single
ephemeral cluster's lifetime still provides value, not just across
separate runs.

## Common Mistakes

- Setting `max_instances` based on today's typical load without headroom
  for the next peak trading season's expected growth (per the growth
  trend data in
  [`03-current-environment/08-resource-utilization-report.md`](../03-current-environment/08-resource-utilization-report.md)).
- Using aggressive scale-down settings for shuffle-heavy jobs, causing
  worker removal mid-shuffle and forcing expensive task retries — tune
  `graceful_decommission_timeout` and scale-down factors conservatively
  for these job families specifically.

## Production Notes

Load-test autoscaling behavior explicitly for every Tier 1 job family
against simulated peak-trading load in
[`17-performance/`](../17-performance/README.md) before that family's
first production cutover — confirm the cluster actually scales up fast
enough to avoid an SLA breach under a real load spike, not just that the
policy is configured.
