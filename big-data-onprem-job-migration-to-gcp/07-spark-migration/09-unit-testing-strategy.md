# Unit Testing Strategy

**Purpose:** Define what must be unit-tested, how, and to what coverage
standard for every migrated job and the shared library — establishing test
coverage that likely didn't exist on-prem, per the gap identified in
[`01-discovery/questions/06-developers.md`](../01-discovery/questions/06-developers.md)
Q9.
**Owner:** Platform Engineering + Data Engineering (per job).

---

## What "unit test" means in this context

A unit test runs **without a live Spark cluster, without network access,
and without any real GCP service connection** — fast (sub-second per test),
deterministic, and runnable on any engineer's laptop or in CI without
special infrastructure. This is possible because of the dependency
injection and pipeline-step design in
[`08-oop-design-patterns.md`](08-oop-design-patterns.md): individual
transformation functions can be tested against small, in-memory
DataFrames using a local Spark session (`local[2]` master), not a real
Dataproc cluster.

## Required coverage

| Component | Required Coverage |
|---|---|
| Shared library (`dp_spark_common`) | Comprehensive — every public function/class, including edge cases and error paths. This is the highest-leverage, highest-blast-radius code in the entire migration. |
| Every transformation function in a job's `transformations/` module | Every function, including edge cases relevant to the business logic (e.g., zero/negative prices, null zone codes, boundary dates) |
| Job orchestration (`main.py`, pipeline assembly) | Covered by integration tests (see [`10-integration-testing-strategy.md`](10-integration-testing-strategy.md)), not unit tests — this layer's value is in wiring, better validated end-to-end |
| I/O helpers (`io/readers.py`, `io/writers.py`) | Unit-tested for logic (path construction, schema application); actual read/write against real GCS/BigQuery is integration-test scope |

## Example test pattern

See [`examples/test_example_pricing_job.py`](examples/test_example_pricing_job.py)
for a complete working example. Key pattern:

```python
import pytest
from pyspark.sql import SparkSession
from example_pricing_job.transformations.price_calculation import apply_discount_cap

@pytest.fixture(scope="module")
def spark():
    return SparkSession.builder.master("local[2]").appName("unit-tests").getOrCreate()

def test_apply_discount_cap_caps_at_configured_max(spark):
    input_df = spark.createDataFrame(
        [("SKU1", 100.0, 50.0)], ["sku", "base_price", "discount_percent"]
    )
    result = apply_discount_cap(input_df, max_discount_percent=40.0)
    row = result.collect()[0]
    assert row["discount_percent"] == 40.0  # capped, not the raw 50.0
```

## Test data strategy

- Unit tests use **small, explicitly constructed in-memory DataFrames**,
  not samples of real production data — this keeps tests fast,
  deterministic, and free of any PII/sensitive data handling concern.
- Every edge case identified during business logic review (with the job
  owner, per
  [`01-discovery/questions/06-developers.md`](../01-discovery/questions/06-developers.md))
  gets an explicit test case — nulls, zeros, negative values, boundary
  dates, empty DataFrames.

## Coverage enforcement

Unit test coverage is measured and enforced in
[`ci-cd/`](../ci-cd/README.md) — a pull request that drops coverage below
the agreed threshold (recommended: 85%+ for the shared library, 75%+ for
job transformation logic) fails the build, consistent with the CI/CD
quality gates defined there.

## Common Mistakes

- Writing tests that only exercise the "happy path" and skip edge cases —
  the happy path is also the path least likely to have a bug; edge cases
  are where migration-introduced regressions actually hide.
- Testing against a live Spark cluster or real GCS bucket in what's
  labeled a "unit test" — this makes the test slow, flaky, and dependent
  on external state, defeating the purpose of fast, reliable unit-level
  feedback.

## Production Notes

For every Tier 1 job's transformation logic, unit tests should explicitly
encode the business rules confirmed during
[`01-discovery/questions/05-business.md`](../01-discovery/questions/05-business.md)
interviews (e.g., "discount can never exceed 40%") as assertions — this
turns tribal business knowledge into an executable, permanently-enforced
specification.
