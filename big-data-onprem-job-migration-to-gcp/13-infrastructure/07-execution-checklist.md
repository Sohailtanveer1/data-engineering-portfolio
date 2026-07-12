# Infrastructure Execution Checklist (Per Environment)

**Purpose:** A single checklist confirming an environment's core
infrastructure is fully provisioned, validated, and ready to support
migration activity.
**Owner:** Cloud/DevOps (executor).

---

## Checklist — Environment: `_______________`

### Foundation

- [ ] GCP project provisioned per
      [`04-target-architecture/02-landing-zone-and-project-structure.md`](../04-target-architecture/02-landing-zone-and-project-structure.md)
- [ ] Remote state backend configured and confirmed working per
      [`02-backend-and-remote-state.md`](02-backend-and-remote-state.md)
- [ ] Naming/tagging validation confirmed active on all modules per
      [`03-naming-and-tagging-standards.md`](03-naming-and-tagging-standards.md)

### Network (depends on 11-network/ being gated)

- [ ] VPC, subnets, firewall rules applied per
      [`11-network/07-execution-checklist.md`](../11-network/07-execution-checklist.md)

### Security (depends on 10-security/ being gated)

- [ ] IAM, service accounts, KMS, Secret Manager applied per
      [`10-security/08-execution-and-review-checklist.md`](../10-security/08-execution-and-review-checklist.md)

### Storage

- [ ] GCS buckets provisioned per data domain per
      [`04-target-architecture/04-storage-architecture.md`](../04-target-architecture/04-storage-architecture.md)

### Compute

- [ ] Dataproc cluster configurations (Terraform modules) provisioned per
      job family per [`12-cluster-design/`](../12-cluster-design/README.md)
- [ ] Dataproc Metastore provisioned per
      [`08-hive-migration/01-metastore-migration-strategy.md`](../08-hive-migration/01-metastore-migration-strategy.md)

### Orchestration

- [ ] Cloud Composer environment provisioned per
      [`04-target-architecture/06-orchestration-architecture.md`](../04-target-architecture/06-orchestration-architecture.md)

### Warehouse

- [ ] BigQuery datasets provisioned per
      [`04-target-architecture/05-data-warehouse-architecture.md`](../04-target-architecture/05-data-warehouse-architecture.md)

### Validation

- [ ] `terraform plan` shows zero unexpected drift
- [ ] All modules pass `terraform validate` and `terraform fmt -check`
- [ ] Environment promotion gate criteria met per
      [`05-environment-promotion.md`](05-environment-promotion.md)

### Sign-off

- [ ] Reviewed by Cloud/DevOps
- [ ] Reviewed by Platform Engineering
- [ ] For `prod`: second approver sign-off obtained

**Executed by:** ________________ **Date:** ________________
**Reviewed by:** ________________ **Date:** ________________

## Common Mistakes

- Marking an environment "provisioned" based on Terraform apply success
  alone without confirming the resources actually work as intended (e.g.,
  a Dataproc cluster config that applies cleanly but fails to actually
  start a job due to a subnet/firewall misconfiguration).
