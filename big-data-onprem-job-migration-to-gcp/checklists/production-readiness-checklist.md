# Production Readiness Checklist

**Purpose:** Consolidated confirmation that a GCP environment (typically
`prod`) is genuinely ready to receive production data — pulling the key
gate from each relevant phase's own detailed checklist into one view.
**Owner:** Migration Program Lead, signed off by each named phase owner.

---

## Checklist — Environment: `_______________`

### Security
- [ ] [`10-security/08-execution-and-review-checklist.md`](../10-security/08-execution-and-review-checklist.md) passed for every in-scope data domain

### Network
- [ ] [`11-network/07-execution-checklist.md`](../11-network/07-execution-checklist.md) passed

### Infrastructure
- [ ] [`13-infrastructure/07-execution-checklist.md`](../13-infrastructure/07-execution-checklist.md) passed

### Cluster Design
- [ ] Cluster configurations for every job family reviewed and load-tested per [`12-cluster-design/`](../12-cluster-design/README.md) and [`17-performance/`](../17-performance/README.md)

### Monitoring
- [ ] Dashboards live per [`18-monitoring/02-metrics-and-dashboards.md`](../18-monitoring/02-metrics-and-dashboards.md)
- [ ] Alerting tested end-to-end per [`18-monitoring/03-alerting-strategy.md`](../18-monitoring/03-alerting-strategy.md)
- [ ] On-call rotation confirmed per [`18-monitoring/06-on-call-and-escalation.md`](../18-monitoring/06-on-call-and-escalation.md)

### CI/CD
- [ ] Pipelines operational and tested per [`ci-cd/`](../ci-cd/README.md)

### Cost
- [ ] Budget alerts configured per [`19-cost-optimization/06-budget-monitoring-and-alerts.md`](../19-cost-optimization/06-budget-monitoring-and-alerts.md)

## Sign-off

| Area | Owner | Signed Off | Date |
|---|---|---|---|
| Security | | | |
| Network | | | |
| Infrastructure | | | |
| Monitoring | | | |
| Cost | | | |

**This checklist must be fully signed off before the first production
data domain migration begins** — it is a one-time environment gate, not
a per-job gate (per-job gates are in
[`migration-checklist.md`](migration-checklist.md)).
