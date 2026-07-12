# Scheduler Inventory

**Purpose:** Catalog every orchestration mechanism actually in use
(Oozie, Airflow if partially adopted, cron, and any ad-hoc trigger
mechanism) so [`09-composer-migration/`](../../09-composer-migration/README.md)
can plan a complete, not partial, migration to Cloud Composer.
**Owner:** Migration Program Lead, populated with Platform Engineering.
**Inputs:** Oozie coordinator/workflow XML exports, crontab exports from
every edge/gateway node, existing Airflow DAG repository if present.
**Outputs:** Directly scopes [`09-composer-migration/`](../../09-composer-migration/README.md).
**Validation method:** Extract crontab entries from **every** edge/gateway
node individually — cron jobs are notoriously node-local and easy to miss
if only one "primary" edge node is checked.

---

## Scheduler mechanism summary

| Mechanism | # of Jobs Orchestrated | Where Defined | Known Gaps/Risks |
|---|---|---|---|
| Oozie | _(count)_ | Oozie coordinator/workflow XML in `/user/oozie/...` on HDFS | XML workflow logic can encode conditional branching that's easy to lose in translation — see [`questions/06-developers.md`](../questions/06-developers.md) Q1 |
| Airflow (if partially adopted) | _(count)_ | DAG repository (git) | Confirm DAG repo is actually the deployed source of truth, not a stale copy |
| Cron | _(count)_ | Per-node crontab, multiple edge/gateway nodes | Highest risk of undocumented/orphaned jobs — reconcile against `06-job-inventory.md` explicitly |
| Ad-hoc/manual trigger | _(count)_ | No central definition — triggered by a person or an external system call | Hardest to inventory; rely on developer interviews |

## Detailed scheduler inventory table

| Job ID | Mechanism | Definition Location | Trigger Type (time/data-availability/manual) | Dependencies (upstream jobs it waits for) | Failure/Retry Behavior Today | Alerting on Failure? |
|---|---|---|---|---|---|---|
| EX-001 | Oozie coordinator | `/user/oozie/coordinators/pricing_nightly.xml` | Time-based, 01:00 daily | Waits on `inventory_sync_intraday` final run of prior day | 3 retries, 10 min apart | Yes — pages on-call |
| EX-003 | Cron + shell wrapper | `/etc/cron.d/inventory_sync` on `edge-node-03` | Time-based, every 15 min | None | No automatic retry — relies on next scheduled run | No — silent failure until missed-SLA alert |
| EX-006 | Cron | `/etc/cron.d/merch_weekly` on `edge-node-01` | Time-based, weekly | None known | No retry | No |
| EX-008 | Manual/ad-hoc | Triggered via internal admin tool by Data Engineering | Manual | Depends on analyst request | N/A | N/A |

_(Illustrative rows only — populate exhaustively; cross-reference every row
against [`06-job-inventory.md`](06-job-inventory.md) by Job ID.)_

## Data-availability-based (not just time-based) triggers

Explicitly flag any job whose trigger is "run when upstream data lands"
rather than a fixed time — these require Cloud Composer sensor/deferrable
operator patterns (see
[`09-composer-migration/`](../../09-composer-migration/README.md)), not a
simple cron-equivalent schedule translation.

| Job ID | Waits for | How "data ready" is currently detected |
|---|---|---|
| _(fill in)_ | _(e.g., upstream Hive partition existing)_ | _(e.g., `_SUCCESS` marker file check in a shell wrapper)_ |

## Common Mistakes

- Migrating Oozie coordinator time triggers directly to Composer schedules
  while missing the *data-dependency* triggers layered on top in the
  workflow XML — this produces jobs that run on time but before their
  actual input data has landed.
- Undercounting cron — treat "we checked the main scheduler box" as
  insufficient; every node that can run cron must be checked.
- Missing retry/alerting behavior — jobs with **no alerting today** are
  jobs where failures may already be going unnoticed; don't assume "no
  alerts configured" means "never fails."

## Production Notes

Pay special attention to any coordinator/cron job whose dependency chain
touches a Tier 1 job (per
[`02-business-critical-jobs.md`](02-business-critical-jobs.md)) — an
incorrectly translated dependency in Composer for a business-critical chain
is a direct production risk at cutover.
