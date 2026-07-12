# Variables, Connections & Secrets (Composer-Specific)

**Purpose:** Detail the Composer-specific implementation of the
configuration layering model established in
[`04-target-architecture/06-orchestration-architecture.md`](../04-target-architecture/06-orchestration-architecture.md)
and
[`07-spark-migration/05-configuration-management-and-secrets.md`](../07-spark-migration/05-configuration-management-and-secrets.md).
**Owner:** Platform Engineering.

---

## Composer Variables

Used for environment-specific, non-secret values referenced across many
DAGs:

| Variable | Example Value (prod) | Used By |
|---|---|---|
| `gcp_project_id` | `acme-data-platform-prod` | Every DAG |
| `gcp_region` | `us-central1` | Every DAG |
| `artifact_bucket` | `acme-prod-artifacts` | Every DAG submitting a Dataproc job |
| `environment` | `prod` | Every DAG (passed as a job argument) |
| `<job>_version` | `2.3.1` | Per-job, pinned package version per [`07-spark-migration/04-packaging-and-dependency-management.md`](../07-spark-migration/04-packaging-and-dependency-management.md) |

Variables are managed via Terraform
([`13-infrastructure/`](../13-infrastructure/README.md)) as the source of
truth, not manually edited via the Airflow UI in `prod` — manual UI edits
in production are exactly the kind of undocumented, person-dependent
change the migration is meant to eliminate.

## Airflow Connections

Used for external system connection details that aren't secret in
themselves (host, port, connection type) — actual credentials are
resolved via Secret Manager, not stored in the Connection's password
field:

```python
# Connection extras reference a Secret Manager secret name, not a raw credential
Connection(
    conn_id="oms_reconciliation_db",
    conn_type="postgres",
    host="{{ var.value.oms_db_host }}",
    extra={"secret_manager_secret": "oms-db-password-prod"},
)
```

Composer's native Secret Manager backend integration is configured so that
Connections and Variables can transparently resolve from Secret Manager
where needed, without job code needing to call the Secret Manager API
directly for connection-level credentials — reserve direct
`ConfigLoader.get_secret()` calls (per
[`07-spark-migration/05-configuration-management-and-secrets.md`](../07-spark-migration/05-configuration-management-and-secrets.md))
for secrets consumed inside job code itself, not orchestration-layer
connections.

## Secret Manager backend configuration

Composer environments are configured with the Secret Manager backend
enabled (`AIRFLOW__SECRETS__BACKEND`), scoped via IAM to only the specific
secrets that environment's service account needs — following the same
least-privilege principle established in
[`10-security/`](../10-security/README.md).

## Where shared DAG utility code lives

Common DAG-authoring utilities (the standard `default_args` factory, the
`alert_on_task_failure` callback, common Sensor configurations) live in a
shared Python module within the DAG folder structure
(`dags/common/`, per
[`04-target-architecture/06-orchestration-architecture.md`](../04-target-architecture/06-orchestration-architecture.md)
project layout), imported by every DAG file — following the same
don't-repeat-yourself principle as the shared Spark library in
[`07-spark-migration/`](../07-spark-migration/README.md).

## Common Mistakes

- Storing an actual credential value in a Connection's password field
  directly instead of routing through Secret Manager — this is the
  Composer-specific instance of the general plaintext-credential mistake
  flagged throughout this repository.
- Editing Variables or Connections manually via the Composer/Airflow UI in
  `prod` "just this once" — always change via Terraform, so configuration
  state is reproducible and auditable.

## Production Notes

Audit `prod` Composer Variables and Connections periodically against their
Terraform-defined source of truth to detect any manual drift — the same
configuration-drift risk that affected the on-prem platform (per
[`03-current-environment/06-security-configuration-assessment.md`](../03-current-environment/06-security-configuration-assessment.md))
can recur on Composer if manual changes aren't actively guarded against.
