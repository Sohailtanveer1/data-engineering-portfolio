# Scheduling Optimization

**Purpose:** Use job timing itself as a cost lever — off-peak scheduling
where business requirements allow it, and avoiding unnecessary schedule
frequency.
**Owner:** Platform Engineering / Data Engineering.

---

## Off-peak scheduling where SLA permits

For jobs without a hard real-time requirement (most Tier 2/3 jobs), review
whether scheduling can shift to take advantage of any GCP pricing
variability or to reduce contention with Tier 1 jobs during their critical
windows — while Dataproc pricing itself isn't generally time-of-day
variable the way some cloud services are, off-peak scheduling still
reduces contention-driven autoscaling cost spikes when many jobs compete
for capacity simultaneously.

## Reviewing schedule frequency against actual need

| Question | Action if "No" |
|---|---|
| Does this job need to run as frequently as it currently does? | Reduce frequency if business need doesn't require it — every unnecessary run is unnecessary cost |
| Is this job's schedule inherited from an on-prem convention that may no longer be necessary (e.g., "runs hourly because that's always been the queue slot")? | Re-evaluate against actual business requirement from [`01-discovery/questions/05-business.md`](../01-discovery/questions/05-business.md), don't assume the on-prem cadence is optimal |

## Consolidating near-duplicate scheduled jobs

Where dependency analysis
([`02-dependency-analysis/`](../02-dependency-analysis/README.md))
reveals multiple jobs reading largely overlapping source data on similar
schedules, evaluate whether consolidation into a single job (reducing
redundant cluster startup and data read cost) is feasible without
compromising the individual jobs' distinct ownership or logic —
evaluated case by case, not forced uniformly.

## Backfill/reprocessing scheduling

Irregular backfill/reprocessing jobs (per
[`04-target-architecture/03-compute-architecture.md`](../04-target-architecture/03-compute-architecture.md)
Dataproc Serverless pattern) should be explicitly scheduled during known
low-contention windows where possible, avoiding competition with
scheduled production jobs for autoscaling capacity that could otherwise
drive up cluster scale-out cost unnecessarily.

## Common Mistakes

- Preserving an on-prem schedule cadence by default without questioning
  whether it reflects genuine business need or historical accident/legacy
  capacity constraints that no longer apply on GCP.
- Consolidating jobs for cost efficiency in a way that obscures clear
  ownership or complicates the dependency graph, trading a modest cost
  saving for meaningfully increased operational complexity.

## Production Notes

Review actual job schedule frequency against business requirement
explicitly during
[`14-job-migration/05-execution-steps-per-job.md`](../14-job-migration/05-execution-steps-per-job.md)
step 1 (wave assignment) — this is a natural, low-effort point to catch
an opportunity before the job is fully built out on its inherited
schedule.
