# Glossary

**Purpose:** Resolve ambiguity between on-prem Hadoop vocabulary and GCP
vocabulary. Different teams (platform, security, network, business) use
overlapping terms differently — this glossary is the tie-breaker.
**Owner:** Migration Program Lead (any engineer can propose additions via
PR/edit; Program Lead merges).
**Inputs:** Terms that surface confusion in meetings or documents.
**Outputs:** A shared vocabulary referenced by every other document in this
repository.

---

## On-prem ↔ GCP concept mapping

| On-prem concept | Closest GCP equivalent | Important differences |
|---|---|---|
| HDFS | Cloud Storage (GCS) | GCS is object storage, not a POSIX-like filesystem — no rename-is-atomic-move semantics, no native append (relevant to Spark job design, see [`07-spark-migration/`](../07-spark-migration/README.md)) |
| YARN | Dataproc's built-in YARN (on-cluster) *or* Dataproc Serverless | Dataproc clusters still run YARN under the hood; Dataproc Serverless removes cluster/YARN management entirely |
| Hive Metastore (on-prem, e.g. MySQL-backed) | Dataproc Metastore (managed) *or* BigQuery datasets/tables | Choice is per-workload — see [`08-hive-migration/`](../08-hive-migration/README.md) |
| Oozie | Cloud Composer (managed Airflow) | Oozie XML workflows have no direct 1:1 translation; migration is a redesign, not a lift-and-shift — see [`09-composer-migration/`](../09-composer-migration/README.md) |
| Kerberos + Ranger | Cloud IAM + optionally Dataplex policy tags | IAM is resource-based/role-based, not ticket-based; there is no direct Kerberos-ticket equivalent |
| Cluster queues (YARN capacity/fair scheduler) | Dataproc autoscaling policies, or separate ephemeral clusters per workload | Ephemeral clusters often replace the need for queue-based multi-tenancy entirely |
| Cron | Cloud Composer DAG schedules (or Cloud Scheduler for non-Spark triggers) | |
| Sqoop | Dataproc Spark JDBC read/write, or Datastream/Storage Transfer for some sources | Sqoop-specific incremental import features must be reimplemented in Spark or a managed CDC tool |
| Local/edge node shell scripts | Cloud Composer `BashOperator`/`KubernetesPodOperator`, or Cloud Build steps | Edge-node-specific paths and local state must be redesigned — cloud jobs are stateless/ephemeral |
| `hdfs dfs -cp` / DistCp | `gsutil`/Storage Transfer Service, or `gcloud storage`, or Hadoop DistCp with the GCS connector | See [`05-storage-migration/`](../05-storage-migration/README.md) |

## Migration-program-specific terms

| Term | Definition |
|---|---|
| **Wave** | A grouped batch of jobs migrated and cut over together, sequenced by risk/priority. See [`14-job-migration/`](../14-job-migration/README.md). |
| **Cutover** | The act of switching a job (or wave of jobs) from running on-prem to running as the system of record on GCP. |
| **Parallel run** | Running a job on both on-prem and GCP simultaneously, comparing output, before fully cutting over — the primary risk mitigation for business-critical jobs. |
| **Freeze window** | A calendar period (see [`02-migration-charter.md`](02-migration-charter.md)) during which business-critical cutovers are prohibited. |
| **Reconciliation** | The automated comparison of migrated data against its on-prem source to prove correctness. See [`16-data-validation/`](../16-data-validation/README.md). |
| **Phase gate** | The documented exit criteria a phase must meet before dependent phases can begin. See [`04-timeline-and-phases.md`](04-timeline-and-phases.md). |
| **Hypercare** | The defined stabilization period immediately after cutover with elevated monitoring and on-call support. See [`22-hypercare/`](../22-hypercare/README.md). |
| **Business-critical job** | A job whose failure or delay directly and materially impacts revenue, compliance, or customer experience (e.g., pricing, fraud detection, order fulfillment feeds). Enumerated in [`01-discovery/`](../01-discovery/README.md). |
| **RPO** | Recovery Point Objective — maximum acceptable data loss, measured in time, in a disaster scenario. |
| **RTO** | Recovery Time Objective — maximum acceptable downtime in a disaster scenario. |
| **Dependency graph** | The documented set of upstream/downstream systems, jobs, and data a given job depends on or feeds. See [`02-dependency-analysis/`](../02-dependency-analysis/README.md). |
| **Ephemeral cluster** | A Dataproc cluster created for the duration of a single job (or job group) and torn down after — the default pattern recommended in [`12-cluster-design/`](../12-cluster-design/README.md). |
| **Idempotent job** | A job that can be safely re-run against the same input without producing duplicate or incorrect output — a hard requirement for all migrated jobs (see [`07-spark-migration/`](../07-spark-migration/README.md)). |

## Adding to this glossary

If a term causes confusion in a meeting, a document review, or a Slack
thread, add it here in the same PR/change that resolved the confusion. This
glossary should grow throughout the program, not just be written once at
the start.
