# ADR-0001: Full GCP Project Isolation Per Environment

**Status:** Accepted
**Date:** See [`00-project-overview/04-timeline-and-phases.md`](../00-project-overview/04-timeline-and-phases.md) Foundation phase
**Deciders:** Migration Program Lead, Cloud/DevOps, Security Engineering

## Context

The platform needs dev/qa/stage/prod environments. Two structural options
exist: separate GCP projects per environment, or a single shared project
with logical namespacing (prefixed resource names, folder-based
separation within one project).

## Decision

Each environment (dev, qa, stage, prod) is a **fully separate GCP
project**, per
[`04-target-architecture/02-landing-zone-and-project-structure.md`](../04-target-architecture/02-landing-zone-and-project-structure.md).

## Alternatives Considered

| Alternative | Why Not Chosen |
|---|---|
| Single shared project, logical namespacing | IAM boundaries are harder to enforce and audit cleanly within one project; quota/billing separation is much weaker; higher risk of an accidental cross-environment action (e.g., a `dev` script accidentally touching `prod` resources due to a naming typo rather than a hard project boundary) |

## Consequences

**Positive:**
- Clean IAM policy boundaries — a `dev` service account cannot access
  `prod` resources by construction, not just by convention.
- Independent quota management and cost attribution per environment.
- Matches constraint C4 (full environment isolation).

**Negative / Tradeoffs Accepted:**
- More Terraform state files and project-level resources to manage
  (mitigated by the module/environment separation in
  [`13-infrastructure/01-terraform-folder-structure.md`](../13-infrastructure/01-terraform-folder-structure.md)).
- Slightly higher initial setup overhead (4 projects vs. 1) — accepted as
  a one-time cost against the ongoing security/operational benefit.

## Related Documents

[`04-target-architecture/02-landing-zone-and-project-structure.md`](../04-target-architecture/02-landing-zone-and-project-structure.md),
[`13-infrastructure/01-terraform-folder-structure.md`](../13-infrastructure/01-terraform-folder-structure.md),
[`00-project-overview/06-assumptions-and-constraints.md`](../00-project-overview/06-assumptions-and-constraints.md)
(constraint C4)
