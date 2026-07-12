# Post-Implementation Review

**Purpose:** A formal, structured review after a wave (or the full
program) completes hypercare — capturing what worked, what didn't, and
what should change for the next wave or the next migration this company
undertakes.
**Owner:** Migration Program Lead, with participation from every RACI
role.

---

## Review structure

| Section | Questions Covered |
|---|---|
| Timeline | Did this wave/job meet its planned timeline? If not, why — and was the plan wrong, or was execution the issue? |
| Quality | How many issues surfaced during UAT vs. hypercare vs. post-hypercare? What does this distribution suggest about validation rigor at each gate? |
| Cost | Actual cost vs. baseline estimate per [`19-cost-optimization/01-cost-baseline-and-attribution.md`](../19-cost-optimization/01-cost-baseline-and-attribution.md) |
| Process | Which phase documents/runbooks in this repository were most useful? Which were missing or insufficient? |
| People | Was the RACI accurate — did the right people have the right authority at the right time? |
| Business satisfaction | Direct feedback from the Business Owner — not just "no complaints," but an explicit satisfaction check |

## Review format

A structured meeting (not just a written survey) with representatives
from every RACI role involved in the wave — Program Lead, Platform
Engineering, Data Engineering, Security, Network, QA, and the Business
Owner.

## Review cadence

- **Per Tier 1 job**: individual review, given the elevated stakes and
  learning value.
- **Per wave** (Tier 2/3 jobs): a combined review covering the whole wave.
- **Program-level**: a comprehensive review at full program completion,
  synthesizing every wave-level review.

## Output

A written summary, stored in
[`documentation/`](../documentation/README.md), explicitly listing:

1. What went well (worth repeating).
2. What didn't go well (worth changing).
3. Specific, actionable process changes for the next wave — not vague
   sentiments, but concrete adjustments (e.g., "add a specific negative
   test case for X to the standard test suite," "adjust wave sizing for
   job family Y").

## Common Mistakes

- Treating the review as a formality with no real behavior change
  resulting from it — the review only has value if its findings actually
  change how the next wave is executed.
- Only reviewing what went wrong, missing the equally valuable
  documentation of what worked well and should be preserved as future
  waves' approach evolves.

## Production Notes

For the full program-level review, present a summary to the Executive
Sponsor explicitly — this closes the loop on the business case established
in
[`00-project-overview/01-executive-summary.md`](../00-project-overview/01-executive-summary.md),
confirming (or honestly reporting a gap against) the promised outcomes.
