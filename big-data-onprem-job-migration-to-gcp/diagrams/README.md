# diagrams — Diagram Library (Mermaid)

## Purpose

An index of every Mermaid diagram in this repository, organized by topic,
so anyone needing a specific visual doesn't have to remember which phase
document it lives in. Every diagram in this repository is written in
Mermaid (not external image files) so it renders directly in GitHub/any
Markdown viewer and stays version-controlled as text — per the root
[`README.md`](../README.md) requirement that every diagram be created
using Mermaid.

## Owner

Migration Program Lead.

## Diagram index

### Program & organization

| Diagram | Location |
|---|---|
| Phase timeline (Gantt) | [`00-project-overview/04-timeline-and-phases.md`](../00-project-overview/04-timeline-and-phases.md) |
| Organization hierarchy | [`04-target-architecture/02-landing-zone-and-project-structure.md`](../04-target-architecture/02-landing-zone-and-project-structure.md) |

### Architecture (big picture)

| Diagram | Location |
|---|---|
| System context diagram | [`architecture/system-context-diagram.md`](../architecture/system-context-diagram.md) |
| End-to-end data flow | [`architecture/data-flow-diagram.md`](../architecture/data-flow-diagram.md) |
| Full target architecture (detailed) | [`04-target-architecture/01-target-architecture-overview.md`](../04-target-architecture/01-target-architecture-overview.md) |
| Network connectivity | [`04-target-architecture/08-network-architecture-overview.md`](../04-target-architecture/08-network-architecture-overview.md), [`11-network/05-hybrid-connectivity-vpn-interconnect.md`](../11-network/05-hybrid-connectivity-vpn-interconnect.md) |

### Dependency & job graphs

| Diagram | Location |
|---|---|
| Dependency graph template | [`02-dependency-analysis/templates/01-dependency-graph-template.md`](../02-dependency-analysis/templates/01-dependency-graph-template.md) |
| Wave sequencing | [`14-job-migration/02-wave-planning.md`](../14-job-migration/02-wave-planning.md) |

### Process flows

| Diagram | Location |
|---|---|
| Configuration layering model | [`07-spark-migration/05-configuration-management-and-secrets.md`](../07-spark-migration/05-configuration-management-and-secrets.md) |
| Cluster autoscaling / dynamic allocation interaction | [`17-performance/07-executor-sizing-and-dynamic-allocation.md`](../17-performance/07-executor-sizing-and-dynamic-allocation.md) |
| Watermark-based incremental load sequence | [`06-data-migration/02-incremental-load-strategy.md`](../06-data-migration/02-incremental-load-strategy.md) |
| Storage migration batching | [`06-data-migration/01-historical-data-migration-plan.md`](../06-data-migration/01-historical-data-migration-plan.md) |
| Validation framework architecture | [`16-data-validation/01-validation-framework-architecture.md`](../16-data-validation/01-validation-framework-architecture.md) |
| Environment promotion flow | [`13-infrastructure/05-environment-promotion.md`](../13-infrastructure/05-environment-promotion.md), [`ci-cd/06-environment-promotion-and-release.md`](../ci-cd/06-environment-promotion-and-release.md) |
| CI/CD pipeline stages | [`ci-cd/02-pipeline-architecture.md`](../ci-cd/02-pipeline-architecture.md) |

### Go-live

| Diagram | Location |
|---|---|
| Go-live phase timeline | [`21-cutover/01-go-live-plan.md`](../21-cutover/01-go-live-plan.md) |
| Deployment sequence (multi-job wave) | [`21-cutover/05-deployment-sequence.md`](../21-cutover/05-deployment-sequence.md) |
| Issue lifecycle | [`documentation/issue-tracker.md`](../documentation/issue-tracker.md) |

## Diagram conventions

- Every diagram uses **Mermaid** syntax (`flowchart`, `sequenceDiagram`,
  `gantt`) directly embedded in its owning Markdown file — never an
  external image.
- Diagrams stay next to the content they illustrate; this index only
  links to them, it doesn't duplicate them, to avoid drift between two
  copies of the same diagram.
- When adding a new diagram anywhere in this repository, add an entry
  here so it stays discoverable.
