# Recovery Testing

**Purpose:** Confirm the platform recovers correctly from realistic
failure scenarios — cluster failure, Composer environment issue, network
interruption — validating the HA and rollback designs from
[`12-cluster-design/05-high-availability-design.md`](../12-cluster-design/05-high-availability-design.md)
and
[`14-job-migration/06-rollback-procedures.md`](../14-job-migration/06-rollback-procedures.md)
actually work, not just that they're documented.
**Owner:** Platform Engineering, run in `stage`.

---

## Recovery test scenarios

| Scenario | Expected Recovery Behavior | Validates |
|---|---|---|
| Dataproc master node failure (HA-mode persistent cluster) | Automatic failover to a surviving master, no job disruption | [`12-cluster-design/05-high-availability-design.md`](../12-cluster-design/05-high-availability-design.md) |
| Ephemeral cluster creation failure (simulated quota/API error) | Composer task fails cleanly, retries per policy, alerts fire | [`09-composer-migration/05-monitoring-retries-and-alerts.md`](../09-composer-migration/05-monitoring-retries-and-alerts.md) |
| Mid-job worker preemption | Task automatically retried on remaining capacity, job completes correctly (idempotently) despite the interruption | [`07-spark-migration/07-idempotency-design.md`](../07-spark-migration/07-idempotency-design.md), [`12-cluster-design/04-preemptible-and-spot-strategy.md`](../12-cluster-design/04-preemptible-and-spot-strategy.md) |
| VPN/Interconnect connectivity interruption mid-sync | Incremental sync resumes correctly without data loss or duplication once connectivity restores | [`05-storage-migration/04-incremental-sync-strategy.md`](../05-storage-migration/04-incremental-sync-strategy.md) |
| Job-level post-cutover rollback | On-prem job re-enabled correctly, downstream consumers redirected, no data gap | [`14-job-migration/06-rollback-procedures.md`](../14-job-migration/06-rollback-procedures.md) |
| Streaming job restart from checkpoint | Job resumes from last checkpoint with no duplicate or missed records | [`07-spark-migration/07-idempotency-design.md`](../07-spark-migration/07-idempotency-design.md) |

## Recovery time measurement

For every scenario, measure and record actual recovery time against the
RTO target established in
[`01-discovery/inventories/05-disaster-recovery-rpo-rto.md`](../01-discovery/inventories/05-disaster-recovery-rpo-rto.md)
— a recovery mechanism that technically works but takes longer than the
required RTO is a gap requiring remediation, not a passed test.

## Testing cadence

Recovery testing runs once per Tier 1 job family before its first
production cutover, and periodically thereafter (e.g., quarterly) as part
of ongoing platform resilience validation, not just a one-time migration
gate.

## Common Mistakes

- Testing recovery mechanisms only in isolation (e.g., testing HA failover
  alone) without testing the combination that actually occurs in a real
  incident (e.g., failover happening mid-job, not at a quiet moment).
- Measuring "did it recover" without measuring "how long did it take" —
  the RTO comparison is what makes this test meaningful, not just a
  binary pass/fail.

## Production Notes

For every Tier 1 job, recovery test results and measured recovery times
must be reviewed and explicitly accepted by the Migration Program Lead as
meeting the RTO requirement before that job proceeds to
[`20-uat/`](../20-uat/README.md).
