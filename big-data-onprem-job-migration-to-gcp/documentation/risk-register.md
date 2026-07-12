# Risk Register (Full, Actively-Managed)

**Purpose:** The complete, living risk register — the source
[`00-project-overview/07-risk-register-summary.md`](../00-project-overview/07-risk-register-summary.md)
summarizes from. Every risk here uses the format from
[`templates/risk-register-entry-template.md`](../templates/risk-register-entry-template.md).
**Owner:** Migration Program Lead.

---

## Active risks

_(Populate using
[`templates/risk-register-entry-template.md`](../templates/risk-register-entry-template.md)
per risk. The top 10 program-level risks are pre-populated below from
[`00-project-overview/07-risk-register-summary.md`](../00-project-overview/07-risk-register-summary.md);
add job-specific and phase-specific risks as they're identified
throughout execution.)_

| Risk ID | Description | Likelihood | Impact | Status | Owner |
|---|---|---|---|---|---|
| R1 | Undiscovered job/data dependencies cause a production incident post-cutover | High | High | Open — mitigated by [`02-dependency-analysis/`](../02-dependency-analysis/README.md) | Program Lead / Platform Eng |
| R2 | Data correctness regression not caught before cutover | Medium | Critical | Open — mitigated by [`16-data-validation/`](../16-data-validation/README.md) | Data Eng |
| R3 | Cutover during peak trading causes revenue-impacting incident | Low | Critical | Mitigated — freeze windows enforced per charter | Program Lead / Business Owner |
| R4 | Cost overrun from mis-sized clusters or storage | Medium | Medium | Open — monitored per [`19-cost-optimization/`](../19-cost-optimization/README.md) | Cloud/DevOps |
| R5 | Security model gap vs. on-prem controls | Medium | Critical | Open — closed per-domain via [`10-security/08-execution-and-review-checklist.md`](../10-security/08-execution-and-review-checklist.md) | Security |
| R6 | Spark/Hive version upgrade surfaces breaking changes | High | Medium | Open — mitigated by [`07-spark-migration/02-spark-version-and-api-migration.md`](../07-spark-migration/02-spark-version-and-api-migration.md) | Platform Eng |
| R7 | Orchestration logic encodes undocumented business rules | Medium | High | Open — mitigated by [`09-composer-migration/01-oozie-to-composer-conversion.md`](../09-composer-migration/01-oozie-to-composer-conversion.md) | Data Eng |
| R8 | Key personnel leave mid-migration with undocumented knowledge | Medium | High | Open — mitigated by Discovery documentation-first approach | Program Lead |
| R9 | Network connectivity delayed by procurement lead times | Medium | Medium | Open — see [`11-network/05-hybrid-connectivity-vpn-interconnect.md`](../11-network/05-hybrid-connectivity-vpn-interconnect.md) | Network |
| R10 | Parallel-run costs exceed budget if timelines slip | Medium | Medium | Open — capped duration per [`14-job-migration/04-parallel-run-strategy.md`](../14-job-migration/04-parallel-run-strategy.md) | Program Lead |

## Review cadence

Reviewed at every phase gate per
[`00-project-overview/04-timeline-and-phases.md`](../00-project-overview/04-timeline-and-phases.md),
and whenever a new risk is identified during execution — new risks are
added using the template, not informally noted elsewhere.

## Closed risks

_(Move a risk here once mitigated/resolved, retaining the record rather
than deleting it — a closed risk's history is useful input for
[`22-hypercare/06-lessons-learned-and-closeout.md`](../22-hypercare/06-lessons-learned-and-closeout.md).)_

| Risk ID | Description | Resolution | Date Closed |
|---|---|---|---|
