# Onboarding Guide

**Purpose:** Get a new team member — engineer, QA, or otherwise —
productive on this migration program within their first week.
**Audience:** Anyone newly joining the migration program.

---

## Day 1: Understand the program

1. Read the root [`README.md`](../README.md) — 15 minutes, gives you the
   full repository map.
2. Read
   [`00-project-overview/01-executive-summary.md`](../00-project-overview/01-executive-summary.md)
   — why this migration is happening.
3. Read
   [`00-project-overview/02-migration-charter.md`](../00-project-overview/02-migration-charter.md)
   — what's in and out of scope.
4. Skim
   [`00-project-overview/05-glossary.md`](../00-project-overview/05-glossary.md)
   — bookmark it; you'll come back to it.

## Day 2-3: Understand where you fit

- Check [`00-project-overview/03-raci-matrix.md`](../00-project-overview/03-raci-matrix.md)
  for your role's responsibilities.
- Check [`MIGRATION-PROGRESS.md`](../MIGRATION-PROGRESS.md) to see current
  program status.
- Meet your team lead and confirm which phase(s)/job(s) you'll be working
  on first.

## Day 3-5: Role-specific deep dive

| Your Role | Start Here |
|---|---|
| Data/Platform Engineer | [`documentation/developer-guide.md`](developer-guide.md) |
| QA | [`15-testing/README.md`](../15-testing/README.md) and [`16-data-validation/README.md`](../16-data-validation/README.md) |
| Cloud/DevOps | [`13-infrastructure/README.md`](../13-infrastructure/README.md) and [`ci-cd/README.md`](../ci-cd/README.md) |
| Security Engineering | [`10-security/README.md`](../10-security/README.md) |
| Network Engineering | [`11-network/README.md`](../11-network/README.md) |

## Access checklist

- [ ] GitHub/repository access to relevant repos
- [ ] GCP project access (per
      [`10-security/02-service-account-strategy.md`](../10-security/02-service-account-strategy.md) —
      human access is scoped per environment, `prod` is break-glass only)
- [ ] Added to the relevant Google Group(s) per
      [`10-security/01-iam-design.md`](../10-security/01-iam-design.md)
- [ ] Added to the relevant on-call rotation if applicable, per
      [`18-monitoring/06-on-call-and-escalation.md`](../18-monitoring/06-on-call-and-escalation.md)
- [ ] Access to the command center communication channel

## Who to ask

Per the RACI escalation path in
[`00-project-overview/03-raci-matrix.md`](../00-project-overview/03-raci-matrix.md)
— when in doubt, ask your team lead first, who will route you correctly.
