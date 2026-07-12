# Packaging & Dependency Management

**Purpose:** Define how job code and the shared library are built,
versioned, and published for consumption by Dataproc — replacing the
manual JAR-staging patterns found in
[`02-dependency-analysis/methodology/03-jar-library-shared-utility-dependencies.md`](../02-dependency-analysis/methodology/03-jar-library-shared-utility-dependencies.md)
findings.
**Owner:** Platform Engineering, integrated with
[`ci-cd/`](../ci-cd/README.md).

---

## Build tooling standard

| Language | Build Tool | Packaging Output |
|---|---|---|
| PySpark | `poetry` or `pip` + `build`, producing a wheel/zip | `.zip` of the package (for `python_file_uris`) or a wheel installed via a Dataproc custom image/init action for heavier dependency sets |
| Scala/Java | `sbt` (Scala) or `maven` (Java), producing a fat/uber JAR (via `sbt-assembly` or `maven-shade-plugin`) | Single self-contained JAR including all non-provided dependencies |

## Versioning standard

All artifacts (job packages and the shared library) use **semantic
versioning** (`MAJOR.MINOR.PATCH`):

- **MAJOR** — breaking change to a public interface (shared library) or a
  business-logic behavior change requiring explicit re-validation (job
  package).
- **MINOR** — backward-compatible new functionality.
- **PATCH** — bug fixes, no interface change.

Every job's Composer DAG references a **specific pinned version** of both
its own job package and the shared library (see the `{{ var.value.*_version
}}` pattern in
[`03-dataproc-submission-patterns.md`](03-dataproc-submission-patterns.md))
— never `latest`. This ensures a shared library release can never silently
change behavior for a job that hasn't explicitly opted into the new
version, directly limiting the blast radius risk called out in the folder
README.

## Artifact storage

| Artifact Type | Storage Location |
|---|---|
| Shared library releases | Artifact Registry (Python package repository or generic repository, per language) |
| Job packages | GCS artifact bucket (`gs://<company>-<env>-artifacts/jobs/<job-name>/<version>/`), published by [`ci-cd/`](../ci-cd/README.md) on merge to the release branch |
| Dataproc custom images (if used) | Artifact Registry (container/image repository) |

## Dependency management within a job

```toml
# pyproject.toml excerpt for a job package
[tool.poetry.dependencies]
python = "^3.10"
dp-spark-common = "2.3.1"   # pinned, exact shared library version

[tool.poetry.group.dev.dependencies]
pytest = "^7.4"
pyspark = "3.5.0"            # matches the target Dataproc image's Spark version exactly
```

Pinning the local development `pyspark` version to exactly match the
target Dataproc image's Spark version (not just "a recent 3.x") is
required — this is what allows
[`09-unit-testing-strategy.md`](09-unit-testing-strategy.md) and
[`10-integration-testing-strategy.md`](10-integration-testing-strategy.md)
tests to catch version-specific behavioral issues before deployment,
rather than only discovering them on the actual cluster.

## Dependency conflict resolution

Per the shared-library reuse ranking built in
[`02-dependency-analysis/`](../02-dependency-analysis/README.md), any
version conflict between jobs sharing a dependency must be resolved before
both jobs can safely run against the same Dataproc image/init-action
baseline — track unresolved conflicts explicitly and prioritize resolving
conflicts affecting the most jobs first.

## Common Mistakes

- Referencing `latest` or an unpinned version for the shared library in
  any production DAG — this defeats the entire purpose of the blast-radius
  containment the versioning standard is designed to provide.
- Building and testing against a different Spark version locally than
  what's actually deployed on the target Dataproc image — this creates a
  false sense of confidence from tests that don't actually exercise the
  real runtime behavior.

## Production Notes

Maintain a **rollback-ready** prior version of the shared library and every
Tier 1 job package readily available in Artifact Registry/GCS at all
times — a version pin only protects you if the previous known-good version
is still there to pin back to.
