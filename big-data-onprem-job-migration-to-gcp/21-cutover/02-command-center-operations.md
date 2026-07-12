# Command Center Operations

**Purpose:** Define roles, staffing, and decision authority during an
active cutover window — a dedicated, focused operating mode distinct from
normal on-call.
**Owner:** Migration Program Lead.

---

## Command center roles

| Role | Responsibility | Filled By |
|---|---|---|
| Command Center Lead | Overall coordination, go/no-go and rollback decisions | Migration Program Lead |
| Technical Executor | Runs the actual deployment sequence steps | Platform Engineering |
| Validation Lead | Runs and interprets post-cutover validation | Data Engineering / QA |
| Business Liaison | Represents the Business Owner, confirms business-side observations | Business Owner or delegate |
| Communications Lead | Sends status updates per the communication plan | Migration Program Lead or delegate |
| On-Call Escalation | Available if the cutover triggers a broader platform issue | Platform on-call (per [`18-monitoring/06-on-call-and-escalation.md`](../18-monitoring/06-on-call-and-escalation.md)) |

## Command center operating model

- **Dedicated communication channel** (a specific Slack channel/bridge
  call) for the duration of the cutover window — not scattered across
  normal channels.
- **Status update cadence**: every 30 minutes during active execution, or
  immediately upon any significant event (step complete, issue
  encountered, decision made).
- **Single decision authority**: the Command Center Lead makes the
  go/no-go and rollback calls, consulting others but not requiring
  consensus that could delay a time-sensitive decision — per the RACI's
  standing authority during cutover.

## Command center timeline

| Phase | Activity |
|---|---|
| T-30 min | Command center convenes, final systems check |
| T-0 | Deployment sequence begins per [`05-deployment-sequence.md`](05-deployment-sequence.md) |
| During execution | Step-by-step status updates, immediate escalation of any deviation from plan |
| Post-execution | Post-cutover validation per [`07-post-cutover-validation.md`](07-post-cutover-validation.md) |
| Stand-down | Command center formally stands down once validation passes and initial monitoring period is stable; transitions to elevated hypercare monitoring |

## Common Mistakes

- Running a Tier 1 cutover without a dedicated command center, treating it
  as a routine deployment — the coordination and fast-decision-making
  structure is what prevents a minor issue from becoming a prolonged
  incident.
- Diffusing decision authority across too many people, causing delay at
  exactly the moment a fast rollback decision might be needed.

## Production Notes

For a multi-job wave cutover, the command center tracks each job's status
independently — a problem with one job in the wave shouldn't be
conflated with or block the others unless there's a genuine shared
dependency.
