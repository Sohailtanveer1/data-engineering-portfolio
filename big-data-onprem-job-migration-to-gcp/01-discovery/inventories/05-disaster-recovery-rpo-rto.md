# Disaster Recovery, RPO & RTO Inventory

**Purpose:** Document current DR posture and required RPO/RTO per data
domain/job tier, so the target GCP architecture can be explicitly designed
to meet (or deliberately and knowingly not meet, with sign-off) these
targets — rather than inheriting an ad-hoc DR posture by accident.
**Owner:** Migration Program Lead, populated with Platform Engineering and
ratified by the Business Owner and Executive Sponsor for each tier.
**Inputs:** [`questions/02-platform-team.md`](../questions/02-platform-team.md)
Q7, business interviews, any existing DR test records.
**Outputs:** Directly shapes [`04-target-architecture/`](../../04-target-architecture/README.md)
(multi-region/multi-zone decisions), [`05-storage-migration/`](../../05-storage-migration/README.md)
(GCS storage class and replication), and
[`12-cluster-design/`](../../12-cluster-design/README.md) (HA cluster
requirements).
**Validation method:** For "current RPO/RTO," do not accept the documented
target if it has never been tested — mark it explicitly as "untested" and
treat the *actual* recoverability as unknown until proven.

---

## Definitions

- **RPO (Recovery Point Objective):** maximum acceptable data loss,
  measured in time (e.g., "RPO of 1 hour" means we can tolerate losing up
  to the last hour of data in a disaster).
- **RTO (Recovery Time Objective):** maximum acceptable time to restore
  service after a disaster.

## Current on-prem DR posture (as-is)

| Component | Current DR Mechanism | Documented RPO | Documented RTO | Last Tested | Actual Outcome if Tested |
|---|---|---|---|---|---|
| HDFS data | _(e.g., no cross-site replication / nightly backup to tape)_ | _(fill in)_ | _(fill in)_ | _(date or "never")_ | _(fill in)_ |
| Hive Metastore (metadata) | _(e.g., MySQL replica, backup schedule)_ | _(fill in)_ | _(fill in)_ | _(date or "never")_ | _(fill in)_ |
| Scheduler state (Oozie/Airflow/cron definitions) | _(fill in)_ | _(fill in)_ | _(fill in)_ | _(fill in)_ | _(fill in)_ |
| Job code / shared libraries | _(e.g., version control — likely low risk)_ | _(fill in)_ | _(fill in)_ | _(fill in)_ | _(fill in)_ |

**If "Last Tested" is "never" for any row, that row's documented RPO/RTO
must be treated as aspirational, not actual, until Discovery explicitly
flags this as a gap to the Executive Sponsor.**

## Required RPO/RTO per criticality tier (target state)

| Criticality Tier (from [`02-business-critical-jobs.md`](02-business-critical-jobs.md)) | Required RPO | Required RTO | Rationale |
|---|---|---|---|
| Tier 1 — Business-Critical | ≤ 1 hour (target; confirm with business) | ≤ 4 hours | Direct revenue/compliance/customer impact if unavailable longer |
| Tier 2 — Business-Important | ≤ 24 hours | ≤ 24 hours | Manual workaround tolerance exists but shouldn't be relied on for multiple days |
| Tier 3 — Standard | ≤ 7 days | ≤ 7 days (best effort) | Internal analytics; low urgency |
| Tier 4 — Retirement candidate | N/A | N/A | Not migrated / no DR commitment |

_(These targets must be explicitly confirmed with the Executive Sponsor and
affected Business Owners — do not treat the above as final without
sign-off; they are proposed defaults based on tier definitions.)_

## Gap analysis: current vs. required

| Tier | Current RPO/RTO (actual, tested where possible) | Required RPO/RTO | Gap? | Action |
|---|---|---|---|---|
| Tier 1 | _(fill in)_ | ≤1h / ≤4h | _(fill in)_ | If gap exists, this is a primary driver for [`04-target-architecture/`](../../04-target-architecture/README.md) multi-region design |

## How GCP changes the DR conversation

Unlike the on-prem cluster (a single physical location, single point of
failure by construction), GCP-native DR options should be evaluated
explicitly in [`04-target-architecture/`](../../04-target-architecture/README.md):

- GCS multi-region or dual-region buckets for storage-layer resilience.
- Dataproc clusters are inherently ephemeral/recreatable from Terraform —
  compute-layer DR becomes "redeploy from IaC," not "restore from backup."
- Dataproc Metastore / managed services carry their own SLA and backup
  characteristics that must be evaluated against the required RTO/RPO
  above, not assumed sufficient by default.

## Common Mistakes

- Treating "the data is in GCS, which has 11 nines of durability" as
  equivalent to "we have a tested DR plan" — durability against object loss
  is not the same as recoverability from a logical error (bad job
  overwriting good data) or a regional outage.
- Setting RPO/RTO targets without involving the business owners who'll
  actually judge whether a 4-hour outage was acceptable.

## Production Notes

Tier 1 RPO/RTO targets should be stress-tested against the actual
after-hours support model — a 4-hour RTO target is not credible if the
on-call rotation's actual response time is longer than that.
