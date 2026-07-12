# Elevated Monitoring Plan

**Purpose:** Define exactly what "elevated" monitoring means during
hypercare, for how long, and the specific criteria for exiting back to
standard monitoring.
**Owner:** Migration Program Lead / Platform Engineering.

---

## What's elevated during hypercare

| Area | Standard Operation | Hypercare (Elevated) |
|---|---|---|
| Monitoring review | Passive — respond to alerts | Active — daily review of dashboards even without an alert firing |
| On-call coverage | Standard rotation | Dedicated engineer actively watching during the job's run window, per [`18-monitoring/06-on-call-and-escalation.md`](../18-monitoring/06-on-call-and-escalation.md) |
| Validation | Standard continuous validation frequency (per tier, per [`16-data-validation/07-continuous-validation-in-production.md`](../16-data-validation/07-continuous-validation-in-production.md)) | Every run validated, regardless of tier |
| Alert threshold sensitivity | Calibrated to steady-state baseline | Tighter thresholds, tuned looser progressively as a stable baseline is established |
| Business Owner check-in | As needed | Scheduled (e.g., daily or every-other-day for Tier 1) |

## Duration by tier

| Tier | Standard Hypercare Duration | Extension Trigger |
|---|---|---|
| Tier 1 | 4 weeks minimum, extended to cover at least one high-complexity operational cycle (month-end, peak period) | Any unresolved issue or open question resets/extends the clock |
| Tier 2 | 2 weeks | Any unresolved issue extends |
| Tier 3 | 1 week | Any unresolved issue extends |

## Exit criteria

Hypercare ends only when **all** of the following are true:

- [ ] No unresolved P1/P2 incident attributable to the migrated job.
- [ ] Continuous validation pass rate stable and consistent with
      expectations across the full hypercare window.
- [ ] SLA consistently met across the full hypercare window.
- [ ] Business Owner confirms continued satisfaction.
- [ ] Knowledge transfer to standing Operations complete (per
      [`03-knowledge-transfer-and-handover.md`](03-knowledge-transfer-and-handover.md)).
- [ ] For Tier 1: at least one high-complexity operational cycle observed
      and stable.

## Common Mistakes

- Treating hypercare duration as a fixed calendar commitment rather than
  a criteria-based exit — a job with recurring minor issues shouldn't
  exit hypercare just because the standard duration elapsed.
- Reducing monitoring intensity gradually without an explicit checkpoint
  decision, letting elevated monitoring quietly lapse rather than being
  deliberately concluded.

## Production Notes

For Tier 1 jobs specifically, do not schedule the hypercare exit date to
fall within a charter freeze window's approach — build in buffer so the
final stability confirmation and exit decision happens with normal
operational calm, not under the pressure of an approaching peak event.
