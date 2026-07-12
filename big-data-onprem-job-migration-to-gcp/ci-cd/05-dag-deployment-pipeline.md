# DAG Deployment Pipeline

**Purpose:** The concrete pipeline for validating and deploying Composer
DAGs — implementing the standards from
[`09-composer-migration/04-dag-best-practices.md`](../09-composer-migration/04-dag-best-practices.md).
**Owner:** Platform Engineering / Cloud-DevOps.

---

## Pipeline stages

| Stage | What Runs | Gate |
|---|---|---|
| Lint/Format | `black --check`, `flake8` | Fails on violation |
| DAG Parse Validation | `python -c "import <dag_file>"` for every DAG file, confirming it parses without error (no Airflow environment needed for this basic check) | Fails on any import/syntax error |
| Best Practices Check | Automated check against the [`09-composer-migration/04-dag-best-practices.md`](../09-composer-migration/04-dag-best-practices.md) checklist (naming convention, owner/SLA declared, no top-level I/O detected via static analysis) | Fails on violation |
| Unit Tests | Tests for any custom operators/sensors/Python callables (e.g., `decide_review_path` from [`09-composer-migration/01-oozie-to-composer-conversion.md`](../09-composer-migration/01-oozie-to-composer-conversion.md)) | Fails on test failure |
| End-to-End Test (qa) | Full DAG execution in a `qa` Composer environment per [`15-testing/04-end-to-end-testing.md`](../15-testing/04-end-to-end-testing.md) | Fails on any scenario failure |
| Sync to `dev` | Automatic, DAG file copied to the `dev` Composer environment's GCS DAG folder | None |
| Sync to `qa`/`stage`/`prod` | Manual trigger per environment promotion gates | Second approver for `prod` |

## DAG sync mechanism

```bash
gsutil rsync -r ./dags/ gs://<composer-environment-bucket>/dags/
```

DAG deployment for Composer is a **file sync to a GCS bucket**, not a
traditional application deployment — the pipeline's job is to run this
sync only after every gate above passes, and only to the intended
environment's bucket.

## Example workflow reference

See [`workflows/dag-sync.yml`](workflows/dag-sync.yml) for the full
working GitHub Actions implementation.

## Handling the dynamic DAG factory pattern

For the dynamic DAG generation pattern (per
[`09-composer-migration/03-dynamic-dag-generation.md`](../09-composer-migration/03-dynamic-dag-generation.md)),
the pipeline additionally validates that the factory function generates
the expected number of DAGs (matching the job family configuration count)
before sync — catching a factory bug that silently drops a job's DAG from
generation.

## Common Mistakes

- Syncing DAG files directly to `prod` without the parse-validation and
  best-practices-check stages, risking a broken DAG file disrupting the
  entire Composer environment's DAG folder parsing.
- Not testing the dynamic DAG factory's actual generated output count,
  missing a silent regression that drops jobs from the generated set.

## Production Notes

For any DAG affecting a Tier 1 job, require the end-to-end test stage to
pass in `qa` **and** `stage` (not just `qa`) before allowing the manual
`prod` sync trigger to be enabled.
