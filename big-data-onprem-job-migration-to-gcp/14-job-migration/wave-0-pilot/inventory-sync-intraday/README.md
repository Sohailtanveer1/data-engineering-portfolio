# Wave 0 Pilot — `inventory_sync_intraday`

Second real job migration in the Wave 0 pilot — see
[`migration-record.md`](migration-record.md) for the full before/after.
Chosen specifically to exercise a different pattern than
[`../pricing-nightly-batch/`](../pricing-nightly-batch/): high-frequency
cron scheduling (not Oozie), stateful read-modify-write (not a simple
daily overwrite), and a persistent (not ephemeral) Dataproc cluster.

## Contents

| Folder/File | What It Is |
|---|---|
| [`on-prem-source/`](on-prem-source/) | The real job: PySpark 2.4.8 script, shell wrapper, and the actual crontab entry (this job was never in Oozie) |
| [`dependency-analysis.md`](dependency-analysis.md) | Filled-in dependency card, including the "shadow scheduler" finding |
| [`migrated-gcp/`](migrated-gcp/) | Complete migrated job: idempotency control table, negative-quantity guard, Composer DAG on a persistent cluster |
| [`migration-record.md`](migration-record.md) | What changed, why, and validation status |
