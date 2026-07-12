# External Dependencies Inventory

**Purpose:** Catalog every dependency that crosses outside the Hadoop
platform itself — Kafka, external databases, REST APIs, FTP/SFTP, NFS — so
[`02-dependency-analysis/`](../../02-dependency-analysis/README.md) and
[`11-network/`](../../11-network/README.md) account for every integration
that must keep working through and after migration.
**Owner:** Migration Program Lead, populated with Platform Engineering,
Developers, and Networking.
**Inputs:** [`questions/06-developers.md`](../questions/06-developers.md),
[`questions/04-networking-team.md`](../questions/04-networking-team.md),
firewall rule exports, connection string grep across job configs.
**Outputs:** Feeds [`02-dependency-analysis/`](../../02-dependency-analysis/README.md)
and [`11-network/`](../../11-network/README.md) directly.
**Validation method:** Grep actual job configuration files and shell
scripts for hostnames, connection strings, and IP addresses — do not rely
solely on interview recall, since long-lived integrations are often "set
and forgotten."

---

## External dependency inventory

| Dependency | Type | Direction | Used By (Job IDs) | Connection Method | Credentials Storage (current) | GCP Target |
|---|---|---|---|---|---|---|
| Kafka cluster (`kafka-prod-01..05`) | Streaming | Bi-directional | EX-002, others | Kafka client (native protocol) | Kerberos keytab | Confirm: Pub/Sub redesign vs. self-managed Kafka on GCE/Confluent Cloud — decision in `04-target-architecture/` |
| Vendor pricing feed (SFTP) | File transfer | Inbound | EX-001 (upstream) | SFTP, key-based auth | SSH key on edge node | Cloud Storage Transfer + SFTP-compatible ingestion, or Composer SFTP operator |
| Payment gateway reconciliation DB | RDBMS | Inbound | EX-004 (upstream) | Sqoop, JDBC | DB credentials in Sqoop password file (⚠ flag for Secret Manager migration) | Spark JDBC read via Secret Manager-sourced credentials |
| Marketing automation platform | REST API | Outbound | EX-005 (downstream) | HTTPS REST, API key | API key in job config file (⚠ flag) | Same pattern, credentials moved to Secret Manager |
| NFS mount (`/mnt/shared_reference_data`) | Network filesystem | Inbound | Multiple jobs (reference data) | NFS mount on edge/worker nodes | N/A | Migrate reference data into GCS; remove NFS dependency — Dataproc workers should not depend on NFS mounts |
| Internal fraud scoring service | REST API | Outbound | EX-002 (downstream) | HTTPS REST, mTLS | Client cert on edge node | Confirm mTLS equivalent via GCP-native or VPN-based connectivity |

_(Illustrative rows only — populate exhaustively; every connection string,
hostname, and credential reference found in job configs or scripts must
have a corresponding row.)_

## ⚠ Flagged findings requiring immediate attention

Any credential found stored in plaintext in a config file, script, or
Sqoop password file (as flagged with ⚠ above) should be:

1. Logged here with its exact location.
2. Flagged to Security immediately (do not wait for
   [`10-security/`](../../10-security/README.md) to formally start) —
   plaintext credentials are a standing risk independent of the migration
   timeline.
3. Migrated to Secret Manager as part of
   [`07-spark-migration/`](../../07-spark-migration/README.md) packaging
   work, never carried forward as plaintext into the new platform.

## Common Mistakes

- Treating "external dependency" as only meaning other internal company
  systems — third-party SaaS APIs and vendor SFTP feeds are just as
  critical to catalog and are more likely to require **external
  coordination** (vendor needs advance notice of an endpoint/IP change).
- Missing NFS mounts because they're "just infrastructure," not a
  named "system" — NFS dependencies are a common hidden blocker to
  Dataproc migration since Dataproc workers are ephemeral and shouldn't
  depend on persistent network mounts (see
  [`07-spark-migration/`](../../07-spark-migration/README.md)).

## Production Notes

For any vendor/partner SFTP or API integration, identify the **required
advance notice period** for endpoint or IP changes now — some partner
contracts require 30–90 days' notice for connectivity changes, which
becomes a hard input to [`14-job-migration/`](../../14-job-migration/README.md)
wave scheduling for the affected jobs.
