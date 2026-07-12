# Working Reference Code

**Purpose:** Executable, minimal-but-complete reference implementations of
every pattern described in this folder's documentation — not pseudocode.
These files are meant to be copied into the actual
`data-platform-spark-common` shared library repository and a real job
repository as the starting point for migration work, per the project
structure in
[`../01-repository-restructuring.md`](../01-repository-restructuring.md).

## Files

| File | Belongs In | Demonstrates |
|---|---|---|
| [`config_loader.py`](config_loader.py) | `dp_spark_common/config/` | Configuration pattern — see [`../05-configuration-management-and-secrets.md`](../05-configuration-management-and-secrets.md) |
| [`spark_session_factory.py`](spark_session_factory.py) | `dp_spark_common/session/` | Factory pattern — see [`../08-oop-design-patterns.md`](../08-oop-design-patterns.md) |
| [`job_builder.py`](job_builder.py) | `dp_spark_common/pipeline/` | Builder pattern — see [`../08-oop-design-patterns.md`](../08-oop-design-patterns.md) |
| [`retry_decorator.py`](retry_decorator.py) | `dp_spark_common/retry/` | Retry logic — see [`../06-logging-and-error-handling.md`](../06-logging-and-error-handling.md) |
| [`example_pricing_job.py`](example_pricing_job.py) | A job repository's `src/<job_name>/` | A complete job assembled from the above patterns |
| [`test_example_pricing_job.py`](test_example_pricing_job.py) | A job repository's `tests/unit/` | Unit testing pattern — see [`../09-unit-testing-strategy.md`](../09-unit-testing-strategy.md) |

## Running these examples

```bash
pip install pyspark==3.5.0 pytest pyyaml google-cloud-secret-manager
pytest test_example_pricing_job.py -v
```

These files intentionally have minimal external dependencies beyond
PySpark itself so they can be read, run, and understood without needing a
live GCP project — the `SecretManagerClient` and GCS/BigQuery I/O calls are
isolated behind interfaces specifically so they can be exercised in unit
tests without real cloud connectivity (per the dependency-injection
principle in
[`../08-oop-design-patterns.md`](../08-oop-design-patterns.md)).
