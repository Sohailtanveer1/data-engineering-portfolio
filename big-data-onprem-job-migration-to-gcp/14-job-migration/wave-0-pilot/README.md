# Wave 0 Pilot

Real, complete job migrations executed as the pilot wave per
[`14-job-migration/02-wave-planning.md`](../02-wave-planning.md) — each
subfolder is one job, taken all the way from its actual on-prem source
through to a fully migrated, tested GCP implementation.

## Jobs in this wave

| Job | Tier | Status |
|---|---|---|
| [`pricing-nightly-batch/`](pricing-nightly-batch/) | 1 | Code complete — see [`pricing-nightly-batch/migration-record.md`](pricing-nightly-batch/migration-record.md) for validation status |

## Adding another job to this wave

Follow the same structure: `on-prem-source/` (the real original),
`dependency-analysis.md`, `migrated-gcp/` (the full migration), and
`migration-record.md` (what changed and why) — see
[`pricing-nightly-batch/`](pricing-nightly-batch/) as the reference
pattern.
