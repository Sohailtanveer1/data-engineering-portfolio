# RACI Matrix — Migration Program

**Purpose:** Remove ambiguity about who decides, who executes, and who must
be informed, for every major category of decision in this program. This
document exists because the single most common cause of stalled migrations
is a decision sitting idle because nobody was sure who could make it.
**Owner:** Migration Program Lead.
**Inputs:** Org chart, confirmed stakeholder list from
[`01-discovery/`](../01-discovery/README.md).
**Outputs:** A matrix every phase document can be cross-referenced against.
**Prerequisites:** Named individuals (not just roles) must be assigned to
each role before program kickoff.
**Deliverables:** This matrix, circulated and acknowledged by every named
role.
**Validation:** Every role listed below has confirmed (in writing) their
responsibilities as described.
**Common Mistakes:** Assigning "Accountable" to a group instead of a single
named person — accountability that's shared is accountability nobody holds.
**Production Notes:** Data Consumers (Merchandising, Marketing, Finance,
Fraud) are explicitly included — they are frequently left out of technical
migration RACIs and then surprise the program with objections during UAT.

**Legend:** R = Responsible (does the work) · A = Accountable (owns the
outcome, signs off — exactly one A per row) · C = Consulted (input sought
beforehand) · I = Informed (told after the fact)

## Roles referenced

| Role | Typical title in an ecommerce org |
|---|---|
| Exec Sponsor | CTO / VP Engineering / VP Data |
| Program Lead | Principal Data Platform Engineer / Migration Program Lead |
| Platform Eng | Data Platform / Spark / Hadoop engineers |
| Cloud/DevOps | Cloud infrastructure / DevOps / SRE team |
| Security | InfoSec / Security Engineering |
| Network | Network Engineering |
| DBA/Data Eng | Data Engineering (Hive, pipelines) |
| QA | QA / Test Engineering |
| Business Owner | Owner of the business function a job serves (e.g., Fraud, Finance) |
| Data Consumers | Merchandising, Marketing, Finance, Fraud analysts consuming outputs |
| Ops/Hypercare | Production support / NOC |

## Decision matrix

| Decision / Activity | Exec Sponsor | Program Lead | Platform Eng | Cloud/DevOps | Security | Network | Data Eng | QA | Business Owner | Data Consumers | Ops |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Approve migration charter & scope | A | R | C | C | C | C | C | I | C | I | I |
| Approve budget | A | R | I | C | I | I | I | I | I | I | I |
| Job/data inventory sign-off | I | A | R | I | I | I | R | I | C | I | I |
| Target architecture design | I | A | R | R | C | C | C | I | I | I | I |
| IAM / security model design | I | C | C | C | A | I | C | I | I | I | I |
| Network design (VPC, connectivity) | I | C | I | R | C | A | I | I | I | I | I |
| Terraform module design/review | I | A | R | R | C | C | I | I | I | I | I |
| Spark job migration (per job) | I | I | A | C | I | I | R | C | I | I | I |
| Hive → target migration (per table) | I | I | C | I | I | I | A | C | I | I | I |
| Composer DAG design | I | I | A | R | I | I | R | I | I | I | I |
| CI/CD pipeline design | I | A | R | R | C | I | I | C | I | I | I |
| Test strategy & sign-off | I | A | C | C | C | I | C | R | I | I | I |
| Data validation framework | I | A | C | I | I | I | R | R | I | I | I |
| Wave / cutover sequencing | C | A | R | R | I | I | R | C | C | I | C |
| Go/no-go for a cutover wave | C | A | R | R | C | I | R | R | C | I | C |
| UAT acceptance | I | C | I | I | I | I | I | R | A | C | I |
| Cutover execution (command center) | I | A | R | R | C | C | R | R | I | I | R |
| Cutover rollback decision | C | A | R | R | I | I | R | C | I | I | C |
| Cost monitoring & optimization | I | A | R | R | I | I | I | I | I | I | I |
| Hypercare incident triage | I | A | R | R | C | I | R | C | I | I | R |
| Post-implementation review | C | A | R | R | R | R | R | R | C | C | R |
| On-prem decommission approval | A | R | R | R | C | C | I | I | I | I | I |

## Escalation path

If a decision is contested or a required approver is unavailable within an
agreed SLA (default: 2 business days for non-cutover decisions, 4 business
hours during an active cutover), escalate in this order:

1. Program Lead attempts direct resolution with the relevant Consulted/
   Responsible party.
2. If unresolved, Program Lead escalates to the Accountable party's manager.
3. If still unresolved and time-sensitive, Program Lead escalates directly
   to the Executive Sponsor.

During an active cutover window (see
[`21-cutover/`](../21-cutover/README.md)), the Program Lead has standing
authority to make rollback decisions unilaterally per the pre-agreed
rollback criteria — escalation happens *after* a rollback, not before, to
avoid delaying a time-critical safety decision.
