# Regression Testing

**Purpose:** Confirm that a change to the shared library, a job, or a DAG
doesn't silently break previously-validated behavior — critical given the
wide blast radius of shared-library changes flagged throughout
[`07-spark-migration/`](../07-spark-migration/README.md).
**Owner:** QA, automated via [`ci-cd/`](../ci-cd/README.md).

---

## Regression suite composition

- **Shared library regression suite**: the full unit test suite for
  `dp_spark_common` (per
  [`07-spark-migration/09-unit-testing-strategy.md`](../07-spark-migration/09-unit-testing-strategy.md)),
  run against every proposed change before a new library version is
  published.
- **Per-job regression suite**: each job's unit + integration tests,
  re-run whenever the shared library version it depends on is bumped —
  not just when the job's own code changes.
- **Golden dataset comparison**: for Tier 1 jobs, a fixed "golden" input
  dataset with known-correct expected output, re-run on every change to
  detect any behavioral drift, however subtle.

## When regression tests run

| Trigger | Suite Run |
|---|---|
| PR against a job repository | That job's unit + integration suite |
| PR against the shared library | Full shared library suite + every dependent job's suite (cross-repository CI trigger, per [`ci-cd/`](../ci-cd/README.md)) |
| Shared library version bump in a job's dependency pin | That job's full suite, before the version bump PR merges |

## Golden dataset maintenance

Golden datasets are version-controlled alongside test code, with an
explicit, reviewed process for updating expected output when a
**deliberate, approved** behavior change occurs (vs. an unintended
regression) — never silently regenerate golden output to make a failing
test pass without understanding why it changed.

## Common Mistakes

- Only regression-testing the specific job being changed, missing the
  cross-job impact of a shared library change.
- Updating a golden dataset's expected output to match new (possibly
  wrong) actual output without investigating why it changed first.

## Production Notes

For Tier 1 jobs, golden dataset regression tests should include at least
one edge-case scenario (e.g., a known historical month-end anomaly for
finance) in addition to a typical-case scenario, so regression coverage
reflects real operational complexity, not just the easy case.
