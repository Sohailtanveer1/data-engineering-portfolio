# Wave 0 Pilot — `pricing_nightly_batch`

The first real, complete, end-to-end job migration in this program —
proving the full pattern before scaling to the rest of the estate per
[`14-job-migration/02-wave-planning.md`](../../02-wave-planning.md).

## Contents

| Folder/File | What It Is |
|---|---|
| [`on-prem-source/`](on-prem-source/) | The job as it actually runs today: PySpark 2.4.8 script, shell wrapper, Oozie coordinator |
| [`dependency-analysis.md`](dependency-analysis.md) | Filled-in dependency card, real findings |
| [`migrated-gcp/`](migrated-gcp/) | The complete migrated job: restructured package, shared library, unit tests, per-environment config, Composer DAG |
| [`migration-record.md`](migration-record.md) | What changed, why, and honest validation status |

## Quick orientation

Start with [`migration-record.md`](migration-record.md) for the full
before/after picture. Compare
[`on-prem-source/pricing_nightly_batch.py`](on-prem-source/pricing_nightly_batch.py)
against
[`migrated-gcp/src/pricing_nightly_batch/main.py`](migrated-gcp/src/pricing_nightly_batch/main.py)
directly to see the restructuring in practice.
