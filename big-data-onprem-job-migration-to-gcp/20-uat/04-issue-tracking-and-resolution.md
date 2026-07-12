# Issue Tracking & Resolution

**Purpose:** Ensure every issue found during UAT is captured, triaged, and
resolved (or explicitly, knowingly deferred) — not lost in a meeting
conversation or forgotten under schedule pressure.
**Owner:** QA (tracks), Migration Program Lead (triages), Platform
Engineering (resolves).

---

## Issue log fields

| Field | Purpose |
|---|---|
| Issue ID | Unique identifier |
| Job/Domain | Which UAT session found it |
| Description | What the Business Owner observed |
| Severity | Blocking / Non-blocking |
| Root Cause | Once investigated |
| Resolution | What was done |
| Verified By | Who confirmed the fix (should include the Business Owner for blocking issues) |
| Status | Open / In Progress / Resolved / Deferred |

## Triage: blocking vs. non-blocking

| Classification | Definition | Impact on Cutover |
|---|---|---|
| Blocking | The issue means the job doesn't meet its acceptance criteria — a real correctness, completeness, or usability problem | Cutover cannot proceed until resolved and re-verified |
| Non-blocking | A minor issue (e.g., a cosmetic dashboard formatting difference) that doesn't affect correctness or core usability | Logged as a backlog item; cutover can proceed with explicit Business Owner agreement that it's genuinely acceptable to defer |

The Business Owner, not engineering alone, has the final say on whether an
issue is genuinely non-blocking — engineering can recommend a
classification, but the Business Owner's agreement is required, per the
RACI.

## Resolution process for blocking issues

1. Root-cause the issue — trace back to the specific phase/document where
   the underlying gap originated (e.g., a missed business rule in
   [`16-data-validation/04-business-rule-validation.md`](../16-data-validation/04-business-rule-validation.md),
   a data migration format issue per
   [`06-data-migration/06-format-and-compression-strategy.md`](../06-data-migration/06-format-and-compression-strategy.md)).
2. Fix the underlying issue, not just the symptom.
3. Re-run relevant validation (
   [`15-testing/`](../15-testing/README.md),
   [`16-data-validation/`](../16-data-validation/README.md)) to confirm
   the fix.
4. Re-verify specifically with the Business Owner against the original
   acceptance criterion that failed.
5. Update the issue log to Resolved.

## Feeding findings back into the process

Every UAT issue is a signal that an earlier validation gate missed
something — after resolution, note in
[`documentation/`](../documentation/README.md) whether the earlier gate
(testing, data validation) should be strengthened to catch this class of
issue earlier for future job waves, closing the loop rather than treating
each UAT issue as an isolated, one-off fix.

## Common Mistakes

- Fixing a UAT-found issue for the specific job without asking whether
  other already-migrated or upcoming jobs share the same underlying gap.
- Allowing a blocking issue to be silently reclassified as non-blocking
  under schedule pressure without genuine Business Owner agreement.

## Production Notes

For Tier 1 domains, any blocking issue found during UAT should trigger a
brief retrospective question: does this issue's root cause suggest a gap
in [`15-testing/`](../15-testing/README.md) or
[`16-data-validation/`](../16-data-validation/README.md)
that should be strengthened before the *next* Tier 1 job's UAT, not just
fixed for this one.
