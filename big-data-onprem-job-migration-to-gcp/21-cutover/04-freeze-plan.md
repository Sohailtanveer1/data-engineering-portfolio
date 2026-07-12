# Freeze Plan

**Purpose:** Define the change freeze immediately before and after a
cutover — distinct from the broader charter freeze windows
([`00-project-overview/02-migration-charter.md`](../00-project-overview/02-migration-charter.md)),
this is a narrow, cutover-specific freeze protecting the stability of the
system being cut over.
**Owner:** Migration Program Lead.

---

## Freeze scope and duration

| Freeze Type | Duration | Scope |
|---|---|---|
| Pre-cutover freeze | T-3 days to T-0 | No non-essential changes to the job/DAG/infrastructure being cut over, or anything it depends on |
| Post-cutover freeze | T-0 to end of elevated hypercare monitoring (per [`22-hypercare/`](../22-hypercare/README.md)) | No non-essential changes to the newly-cutover job, minimizing variables if an issue needs to be diagnosed |

## What's frozen vs. what's not

| Frozen | Not Frozen |
|---|---|
| Code changes to the job being cut over | Other, unrelated jobs' normal migration work continues |
| Infrastructure changes affecting the job's cluster/DAG/IAM | Other environments (`dev`, `qa`) continue normal development |
| Non-essential shared library changes | A genuine emergency fix, via the expedited change process per [`13-infrastructure/05-environment-promotion.md`](../13-infrastructure/05-environment-promotion.md) |

## Freeze exception process

An emergency change during a freeze window requires:

1. Migration Program Lead approval.
2. Explicit assessment of whether the change affects the cutover's
   stability/rollback capability.
3. Logged in [`logs/`](../logs/README.md) with rationale.

## Common Mistakes

- Freezing too broadly (halting unrelated work platform-wide) when a
  narrowly-scoped freeze would suffice, unnecessarily slowing the overall
  program.
- Freezing too narrowly, missing a shared dependency (e.g., the shared
  Spark library) that could still destabilize the cutover if changed
  during the freeze window.

## Production Notes

For Tier 1 cutovers, explicitly confirm the freeze scope includes every
shared component identified in the job's dependency card (per
[`02-dependency-analysis/templates/02-job-dependency-card-template.md`](../02-dependency-analysis/templates/02-job-dependency-card-template.md))
— a change to a shared library or shared cluster configuration during a
Tier 1 freeze window is exactly the kind of variable that should be
explicitly excluded.
