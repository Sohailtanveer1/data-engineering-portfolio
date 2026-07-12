# ADR-0004: Secret Manager Mandatory, No Plaintext Credentials

**Status:** Accepted
**Date:** See [`00-project-overview/04-timeline-and-phases.md`](../00-project-overview/04-timeline-and-phases.md) Foundation phase
**Deciders:** Migration Program Lead, Security Engineering

## Context

Discovery
([`01-discovery/inventories/12-external-dependencies.md`](../01-discovery/inventories/12-external-dependencies.md))
found multiple credentials stored in plaintext — Sqoop password files,
API keys in job config files. The target platform's credential handling
approach needed to be decided explicitly rather than carried forward.

## Decision

Every credential is stored in Secret Manager and resolved at runtime via
`secret://` references, per
[`07-spark-migration/05-configuration-management-and-secrets.md`](../07-spark-migration/05-configuration-management-and-secrets.md).
No plaintext credential is permitted anywhere in code, config files, or
Composer Variables/Connections — enforced via automated secret scanning
in [`ci-cd/02-pipeline-architecture.md`](../ci-cd/02-pipeline-architecture.md)
as well as code review.

## Alternatives Considered

| Alternative | Why Not Chosen |
|---|---|
| Continue current per-job credential storage patterns | Carries forward a confirmed security exposure identified in Discovery; does not meet the security architecture principles in [`04-target-architecture/07-security-architecture-overview.md`](../04-target-architecture/07-security-architecture-overview.md) |
| Environment variables for secrets (common lightweight pattern) | Environment variables are visible in process listings and easily logged accidentally; Secret Manager provides audit logging, rotation, and IAM-scoped access that environment variables don't |

## Consequences

**Positive:**
- Closes every plaintext-credential finding from Discovery.
- Every secret access is audit-logged per
  [`10-security/05-audit-logging.md`](../10-security/05-audit-logging.md).
- Rotation requires no job redeployment, per
  [`10-security/07-key-rotation.md`](../10-security/07-key-rotation.md).

**Negative / Tradeoffs Accepted:**
- Slight latency overhead per Secret Manager API call — negligible in
  practice for job-startup-time secret resolution, not a per-record
  operation.
- Requires disciplined IAM scoping (per-secret access) to avoid
  recreating an over-broad access pattern within Secret Manager itself —
  addressed explicitly in
  [`10-security/03-secret-manager-design.md`](../10-security/03-secret-manager-design.md).

## Related Documents

[`07-spark-migration/05-configuration-management-and-secrets.md`](../07-spark-migration/05-configuration-management-and-secrets.md),
[`10-security/03-secret-manager-design.md`](../10-security/03-secret-manager-design.md),
[`01-discovery/inventories/12-external-dependencies.md`](../01-discovery/inventories/12-external-dependencies.md)
