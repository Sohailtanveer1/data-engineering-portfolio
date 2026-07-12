# OOP Design Patterns for Shared Spark Utilities

**Purpose:** Define the specific design patterns used in the shared
library and job code — Factory, Builder, and Configuration patterns — with
working reference implementations in [`examples/`](examples/), so every
engineer migrating a job follows the same, reviewed architectural
approach rather than inventing a new pattern per job.
**Owner:** Platform Engineering (shared-library owner role).

---

## Why these specific patterns

Each pattern here solves a concrete problem observed in the current
platform's technical debt (per
[`03-current-environment/09-pain-points-and-bottlenecks.md`](../03-current-environment/09-pain-points-and-bottlenecks.md)
and
[`02-dependency-analysis/`](../02-dependency-analysis/README.md) findings)
— they are not applied for their own sake.

## Factory Pattern — SparkSessionFactory

**Problem it solves:** Inconsistent Spark session creation across jobs
(different config defaults, different handling of GCS connector setup,
different AQE settings) makes behavior unpredictable and hard to reason
about across the estate.

**Pattern:** A single factory class responsible for constructing a
correctly-configured `SparkSession` for every job, so job code never calls
`SparkSession.builder` directly.

See [`examples/spark_session_factory.py`](examples/spark_session_factory.py)
for the full implementation. Usage in job code:

```python
from dp_spark_common.session.factory import SparkSessionFactory

spark = SparkSessionFactory.create(app_name="pricing_nightly_batch", config=config)
```

The factory encapsulates: AQE enablement, GCS/BigQuery connector
configuration, standard shuffle partition defaults (tunable via config, not
hardcoded per job), and consistent Kryo serializer registration.

## Builder Pattern — Job Pipeline Builder

**Problem it solves:** Job `main.py` entry points on-prem often mix
orchestration (what steps run, in what order) with the steps' actual
implementation, making a job's high-level structure hard to read and its
individual steps hard to test in isolation.

**Pattern:** A fluent builder that assembles a job's pipeline as an
explicit, readable sequence of named steps, each independently testable.

See [`examples/job_builder.py`](examples/job_builder.py) for the full
implementation. Usage in a job's `main.py`:

```python
from dp_spark_common.pipeline.builder import PipelineBuilder

pipeline = (
    PipelineBuilder(spark=spark, config=config, logger=logger)
    .add_step("read_source", read_pricing_source)
    .add_step("calculate_prices", calculate_prices)
    .add_step("apply_zone_mapping", apply_zone_mapping)
    .add_step("write_output", write_pricing_output)
    .build()
)
pipeline.run()
```

Each step is a plain function taking and returning a `PipelineContext`
(carrying the current DataFrame(s) and metadata), making steps trivially
unit-testable independent of the full pipeline or a live Spark cluster
connection where the step logic doesn't require one.

## Configuration Pattern — ConfigLoader

**Problem it solves:** Configuration scattered across hardcoded values,
`--conf` flags, and ad-hoc environment variable reads, with no single
place to see what a job depends on configuration-wise or to validate it's
all present.

**Pattern:** Already introduced in
[`05-configuration-management-and-secrets.md`](05-configuration-management-and-secrets.md)
— see [`examples/config_loader.py`](examples/config_loader.py). The key
OOP element is that `ConfigLoader.load()` returns a single, typed,
validated configuration object passed explicitly through the pipeline
(via dependency injection into each step/class), never accessed via global
state or ad-hoc environment variable reads scattered through the codebase.

## Dependency injection, not global state

All three patterns above share a principle: dependencies (Spark session,
config, logger) are **passed explicitly** into the classes/functions that
need them (constructor or function parameters), never accessed via module-
level globals or singletons fetched implicitly deep inside business logic.
This is what makes unit testing possible without a live Spark
cluster/GCP connection — see
[`09-unit-testing-strategy.md`](09-unit-testing-strategy.md).

## Utility classes

Generic, stateless utility functions (date manipulation, string
normalization, common validation helpers) live in the shared library under
a clearly-scoped `utils/` module, organized by concern (not one giant
"Utils" catch-all class) — e.g., `dp_spark_common.utils.dates`,
`dp_spark_common.utils.validation`.

## Common Mistakes

- Building job-specific subclasses of the shared `SparkSessionFactory` or
  `ConfigLoader` to "customize" behavior per job — if a job genuinely needs
  different behavior, that need should be expressed as a configuration
  option in the shared class, not a per-job class hierarchy that
  fragments the shared library's guarantees.
- Using the Builder pattern for a pipeline's *steps* but still reaching
  into global state or hardcoded values *within* an individual step — the
  pattern only delivers its testability benefit if dependency injection is
  followed consistently at every level.

## Production Notes

Changes to the shared library's Factory/Builder/Config classes require the
broadest possible test coverage and the most conservative versioning
discipline (per
[`04-packaging-and-dependency-management.md`](04-packaging-and-dependency-management.md))
in the entire migration — a subtle bug introduced here has the potential to
silently affect every single migrated job simultaneously.
