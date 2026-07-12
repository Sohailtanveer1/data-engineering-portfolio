# Dynamic DAG Generation

**Purpose:** Avoid hand-writing hundreds of near-identical DAG files for
structurally similar job families (e.g., every per-data-domain nightly
batch job follows the same create-cluster → submit → delete-cluster
shape) — a single, parameterized DAG factory generates them all from a
declarative configuration, keeping the pattern consistent and
maintainable at scale.
**Owner:** Platform Engineering.

---

## When to use dynamic generation vs. a hand-written DAG

| Situation | Approach |
|---|---|
| A family of 5+ jobs sharing the same structural pattern (same operator sequence, differing only in parameters like table name, schedule, resource sizing) | Dynamic generation |
| A single job with genuinely unique orchestration logic (complex branching, multiple distinct external integrations) | Hand-written DAG |
| A job that starts as "similar to the family" but is expected to diverge significantly over time | Hand-written DAG, to avoid forcing an awkward abstraction onto a job that doesn't really fit the shared pattern |

## Reference implementation

See [`examples/dynamic_dag_factory.py`](examples/dynamic_dag_factory.py)
for a complete working example generating one DAG per entry in a
declarative job-family configuration list.

```python
# Simplified illustration — see examples/ for the full version
JOB_FAMILY_CONFIG = [
    {"job_name": "pricing_nightly_batch", "schedule": "0 1 * * *", "data_domain": "pricing", "tier": 1},
    {"job_name": "merchandising_weekly_report", "schedule": "0 6 * * 1", "data_domain": "merchandising", "tier": 3},
    # ... one entry per job in the family, sourced from
    # 01-discovery/inventories/06-job-inventory.md
]

for job_config in JOB_FAMILY_CONFIG:
    dag = build_standard_batch_dag(job_config)
    globals()[job_config["job_name"]] = dag  # Airflow discovers DAGs via module globals
```

## Sourcing the configuration from the job inventory

The declarative configuration list driving dynamic generation should be
sourced from (or kept in lockstep with)
[`01-discovery/inventories/06-job-inventory.md`](../01-discovery/inventories/06-job-inventory.md)
— avoid maintaining a second, independent list of jobs that can drift out
of sync with the authoritative inventory. For jobs numbering in the
hundreds, consider generating this configuration list programmatically
from a shared source (e.g., a YAML file checked into the shared library
repo, updated as part of each job's onboarding to the migration).

## Design considerations for the factory function

- **Keep the factory function itself simple and heavily tested** — since
  it generates every DAG in the family, a bug here has the same wide blast
  radius concern as the shared Spark library (see
  [`07-spark-migration/08-oop-design-patterns.md`](../07-spark-migration/08-oop-design-patterns.md)).
- **Parameterize only what genuinely varies** across the family (job name,
  schedule, resource sizing, data domain) — resist parameterizing so much
  that the "shared pattern" becomes meaningless.
- **Support per-job overrides** for the inevitable exceptions (e.g., one
  job in the family needs a longer SLA timeout) without requiring that job
  to be pulled out of dynamic generation entirely — over-parameterize
  slightly rather than fragment the pattern.

## Common Mistakes

- Applying dynamic generation to jobs that don't actually share a common
  structure, forcing an ill-fitting abstraction that becomes harder to
  reason about than separate hand-written DAGs would have been.
- Under-testing the factory function itself — since it's DAG-generating
  code, not a single DAG, a bug affects every generated DAG simultaneously,
  and Airflow's DAG-parsing failure mode (a broken DAG file can prevent
  the whole Composer environment's DAG folder from parsing cleanly,
  depending on the failure) makes this especially high-stakes.

## Production Notes

Roll out dynamic generation first for a batch of Tier 3 jobs to validate
the factory function thoroughly, before applying it to any Tier 1 job
family — consistent with the general "prove the pattern on lower-risk jobs
first" principle used throughout this migration.
