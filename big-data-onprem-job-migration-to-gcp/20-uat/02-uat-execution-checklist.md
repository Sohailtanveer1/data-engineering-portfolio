# UAT Execution Checklist

**Purpose:** Step-by-step process for running UAT, ensuring it's genuine
hands-on business testing, not a passive demo.
**Owner:** QA (facilitates), Business Owner (executes).

---

## Checklist — Job/Domain: `_______________`

### Pre-UAT

- [ ] Acceptance criteria finalized and agreed per
      [`01-acceptance-criteria.md`](01-acceptance-criteria.md)
- [ ] Parallel-run minimum duration met with zero unresolved failures
      per [`14-job-migration/04-parallel-run-strategy.md`](../14-job-migration/04-parallel-run-strategy.md)
- [ ] UAT environment (typically `stage`) has representative data and is
      accessible to the Business Owner
- [ ] Business Owner has access to their actual tooling (BI dashboard,
      query tool) repointed to the migrated data

### UAT session

- [ ] Business Owner directly interacts with the migrated data/tooling
      themselves — not an engineering-led demo
- [ ] Each acceptance criterion explicitly walked through and checked off
- [ ] Business Owner given time to explore beyond the scripted criteria
      (open-ended review), since real-world usage often surfaces things a
      scripted checklist misses
- [ ] Any issue found is logged immediately per
      [`04-issue-tracking-and-resolution.md`](04-issue-tracking-and-resolution.md),
      not just verbally noted

### Post-UAT

- [ ] All logged issues triaged — blocking vs. non-blocking for cutover
- [ ] Blocking issues resolved and re-validated before proceeding
- [ ] Non-blocking issues logged as post-cutover backlog items, with
      Business Owner agreement that they're genuinely non-blocking
- [ ] Sign-off obtained per
      [`03-business-signoff-process.md`](03-business-signoff-process.md)

**UAT conducted by (Business Owner):** ________________
**Facilitated by (QA):** ________________
**Date:** ________________

## Common Mistakes

- Rushing through the scripted acceptance criteria without leaving time
  for open-ended exploration, missing issues a scripted checklist doesn't
  anticipate.
- Letting engineering drive the session ("let me show you this works")
  instead of the Business Owner directly operating the tooling themselves.

## Production Notes

For Tier 1 domains, schedule UAT as a dedicated session (not squeezed into
a status meeting) with the Business Owner's calendar blocked specifically
for it — treating it as a checkbox to rush through undermines its entire
purpose.
