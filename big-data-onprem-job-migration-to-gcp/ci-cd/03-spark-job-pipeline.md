# Spark Job Pipeline

**Purpose:** The concrete pipeline for building, testing, packaging, and
publishing a Spark job or the shared library — implementing
[`07-spark-migration/09-unit-testing-strategy.md`](../07-spark-migration/09-unit-testing-strategy.md),
[`07-spark-migration/10-integration-testing-strategy.md`](../07-spark-migration/10-integration-testing-strategy.md),
and
[`07-spark-migration/04-packaging-and-dependency-management.md`](../07-spark-migration/04-packaging-and-dependency-management.md)
as an automated pipeline.
**Owner:** Platform Engineering / Cloud-DevOps.

---

## Pipeline stages

| Stage | What Runs | Gate |
|---|---|---|
| Lint/Format | `black --check`, `flake8` (Python) or `scalafmt --check` (Scala) | Fails the build on any violation |
| Unit Tests | Full `pytest`/`sbt test` suite, per [`07-spark-migration/09-unit-testing-strategy.md`](../07-spark-migration/09-unit-testing-strategy.md) | Fails on any test failure; coverage threshold enforced |
| Secret Scan | `gitleaks` or equivalent | Fails on any detected credential pattern |
| Build/Package | `poetry build` / `sbt assembly`, producing the versioned artifact per [`07-spark-migration/04-packaging-and-dependency-management.md`](../07-spark-migration/04-packaging-and-dependency-management.md) | Fails on build error |
| Integration Tests | Deploy to a short-lived `qa` Dataproc Serverless batch, run the integration suite per [`07-spark-migration/10-integration-testing-strategy.md`](../07-spark-migration/10-integration-testing-strategy.md) | Fails on any test failure |
| Publish | Upload versioned artifact to Artifact Registry / GCS artifact bucket | Only runs on merge to `main`, never from a feature branch |

## Cross-repository dependency handling

When the shared library (`data-platform-spark-common`) publishes a new
version, its pipeline additionally triggers the full test suite of every
dependent job repository (per the regression testing strategy in
[`15-testing/02-regression-testing.md`](../15-testing/02-regression-testing.md))
— implemented via a repository-dispatch event or equivalent cross-repo
trigger mechanism, ensuring a shared library change can't merge and
publish without confirming it doesn't break dependent jobs.

## Example workflow reference

See [`workflows/spark-job-ci.yml`](workflows/spark-job-ci.yml) for the
full working GitHub Actions implementation of this pipeline.

## Version and tag assignment

Per
[`07-spark-migration/04-packaging-and-dependency-management.md`](../07-spark-migration/04-packaging-and-dependency-management.md)
semantic versioning — the pipeline determines the version bump
(major/minor/patch) from the PR's labeled type (breaking/feature/fix) or
an explicit version bump commit, and tags the release commit accordingly,
feeding
[`06-environment-promotion-and-release.md`](06-environment-promotion-and-release.md).

## Common Mistakes

- Skipping integration tests in the pipeline for "minor" changes — every
  change to code that will run in production should pass the full gate,
  since "minor" is often a judgment made before the actual impact is
  known.
- Publishing an artifact before integration tests pass, allowing a broken
  version to become available for a job's DAG to reference.

## Production Notes

For the shared library specifically, the cross-repository dependent-test
trigger is a mandatory, non-bypassable gate — given its blast radius, no
shared library version should ever be published without confirming it
doesn't break any dependent job.
