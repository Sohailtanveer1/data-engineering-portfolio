# Priority Matrix

**Purpose:** Convert job criticality tier, dependency complexity, and
readiness into an objective wave-assignment score — removing politics and
convenience from wave sequencing.
**Owner:** Migration Program Lead.

---

## Scoring dimensions

| Dimension | Weight | Scoring |
|---|---|---|
| Criticality tier (inverse — lower tier migrates earlier) | High | Tier 3 = 3 pts, Tier 2 = 2 pts, Tier 1 = 1 pt (lower score = earlier wave, since we want low-risk jobs first) |
| Dependency readiness | High | All upstream dependencies already migrated = 3 pts; some pending = 1 pt; blocked = 0 pts (jobs with 0 pts cannot be scheduled) |
| Test/validation coverage | Medium | Full unit+integration+idempotency coverage = 3 pts; partial = 1 pt; none = 0 pts |
| Business urgency (from Discovery interviews) | Medium | No special urgency = 2 pts; moderate = 1 pt; explicit urgent request = 0 pts (schedule per Business Owner's requested timing regardless of default sequencing) |
| Team readiness (owning team available and trained on new patterns) | Low | Ready = 1 pt; not yet = 0 pts |

## Composite score → wave assignment

| Composite Score Range | Wave Assignment |
|---|---|
| 10-12 (highest readiness, lowest risk) | Wave 1 (pilot) |
| 7-9 | Wave 2-3 |
| 4-6 | Wave 4-6 |
| 0-3, or any dependency-blocked job | Not yet schedulable — resolve blockers first |

## Applying the matrix — worked examples

| Job ID | Tier Score | Dependency Score | Test Score | Urgency Score | Team Score | Composite | Wave |
|---|---|---|---|---|---|---|---|
| EX-006 (`weekly_merchandising_adhoc_report`, Tier 3) | 3 | 3 | 3 | 2 | 1 | 12 | Wave 1 (pilot) |
| EX-005 (`marketing_campaign_attribution`, Tier 2) | 2 | 3 | 3 | 1 | 1 | 10 | Wave 1-2 |
| EX-003 (`inventory_sync_intraday`, Tier 1) | 1 | 3 | 3 | 2 | 1 | 10 | Later wave despite high score — Tier 1 jobs get extra deliberate delay regardless of composite score, per the "shrink wave size as tier increases" principle |
| EX-002 (`fraud_score_hourly`, Tier 1) | 1 | 1 | 1 | 2 | 0 | 5 | Blocked — dependency and test coverage gaps must close first |

Note the deliberate override for Tier 1 jobs: even a high composite score
doesn't fast-track a Tier 1 job ahead of the "prove the pattern on lower
tiers first" principle established in
[`07-spark-migration/README.md`](../07-spark-migration/README.md) and
[`09-composer-migration/README.md`](../09-composer-migration/README.md).

## Recalculating scores

This matrix is recalculated **weekly** during active wave planning, not
computed once — dependency readiness and test coverage change as work
progresses, and the wave plan should reflect current reality, not a
stale snapshot.

## Common Mistakes

- Letting the highest composite score alone determine wave order without
  applying the Tier 1 deliberate-delay override.
- Recalculating scores only when a job's status is manually reported,
  instead of on a fixed schedule — this lets the matrix silently go stale.

## Production Notes

Business urgency scores must be confirmed directly with the Business
Owner (per the RACI), not assumed by engineering — a job engineering
assumes is "not urgent" may have an unstated deadline the business hasn't
volunteered unprompted.
