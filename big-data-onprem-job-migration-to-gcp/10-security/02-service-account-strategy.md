# Service Account Strategy

**Purpose:** Define one service account per function (mirroring the
on-prem Kerberos functional-ID pattern from
[`03-current-environment/06-security-configuration-assessment.md`](../03-current-environment/06-security-configuration-assessment.md)),
using Workload Identity Federation rather than distributed key files.
**Owner:** Security Engineering + Platform Engineering.

---

## One service account per job family, not per job or platform-wide

| Granularity | Assessment |
|---|---|
| One service account for the entire platform | Rejected — violates least privilege; a single compromised credential exposes everything |
| One service account per individual job | Rejected — excessive management overhead for hundreds of jobs with largely overlapping access needs |
| **One service account per job family / data domain (recommended)** | Matches the on-prem functional-ID granularity already in use (e.g., `svc_pricing_etl`) and keeps IAM review tractable |

## Naming and inventory

Following the naming convention in
[`04-target-architecture/02-landing-zone-and-project-structure.md`](../04-target-architecture/02-landing-zone-and-project-structure.md):

| Service Account | Purpose | Scope | Migrated From (on-prem) |
|---|---|---|---|
| `svc-pricing-etl@acme-data-platform-prod.iam.gserviceaccount.com` | Pricing Dataproc jobs | Read pricing raw/curated, write pricing curated, read shared zone lookup | `svc_pricing_etl` Kerberos principal |
| `svc-fraud-etl@...` | Fraud Dataproc jobs | Read/write fraud domain, read Kafka/Pub/Sub topic | `svc_fraud_etl` |
| `svc-composer-orchestrator@...` | Composer environment identity | Dataproc job submission/cluster lifecycle only — no direct data-plane access | New (no direct on-prem equivalent — Oozie ran under individual job identities) |
| `svc-ci-cd-deploy@...` | CI/CD pipeline (Terraform apply, artifact publish) | Scoped to infrastructure and artifact management only, never production data | New |

_(Populate exhaustively from
[`01-discovery/inventories/11-storage-inventory.md`](../01-discovery/inventories/11-storage-inventory.md)
service account inventory and
[`03-current-environment/06-security-configuration-assessment.md`](../03-current-environment/06-security-configuration-assessment.md).)_

## Authentication: Workload Identity Federation, not distributed keys

Dataproc clusters and Composer environments use **attached service
account identity** — Dataproc VMs and Composer workers authenticate as
their assigned service account natively, with no downloaded JSON key file
ever distributed to a node or embedded in code. This eliminates an entire
category of on-prem risk (keytab distribution and potential leakage,
flagged in
[`01-discovery/questions/03-security-team.md`](../01-discovery/questions/03-security-team.md)).

For any external system requiring a GCP identity outside GCP's own compute
(e.g., a CI/CD runner outside GCP), use Workload Identity Federation to
exchange an external identity token for short-lived GCP credentials —
never a long-lived downloaded service account key, except in the rare,
explicitly-justified case where no federation path exists, and even then
with mandatory rotation per
[`07-key-rotation.md`](07-key-rotation.md).

## Common Mistakes

- Creating and downloading a service account JSON key "for local testing"
  and leaving it on a laptop or committed to a repository — this is
  explicitly prohibited; use `gcloud auth application-default login` with
  the engineer's own scoped access for local development instead.
- Sharing one service account across multiple, functionally distinct job
  families "to reduce IAM management overhead" — this collapses the
  least-privilege boundary the per-family design is meant to provide.

## Production Notes

Every service account request for a new job family must go through
Security Engineering review before creation — service account sprawl
without review is how least-privilege design erodes over time.
