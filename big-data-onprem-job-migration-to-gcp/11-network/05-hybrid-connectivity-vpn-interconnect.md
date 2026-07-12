# Hybrid Connectivity — VPN vs. Interconnect

**Purpose:** Resolve open decision O1 from
[`04-target-architecture/09-architecture-decision-log.md`](../04-target-architecture/09-architecture-decision-log.md)
— the final connectivity method between on-prem and GCP — using measured
requirements rather than a default assumption.
**Owner:** Network Engineering, approved by Migration Program Lead given
the schedule-risk implications.

---

## Decision inputs

| Input | Source |
|---|---|
| Total effective data volume requiring transfer | [`01-discovery/inventories/11-storage-inventory.md`](../01-discovery/inventories/11-storage-inventory.md) |
| Sustained parallel-run bandwidth requirement (ongoing incremental sync across all in-flight domains) | [`06-data-migration/02-incremental-load-strategy.md`](../06-data-migration/02-incremental-load-strategy.md) aggregate across active domains |
| Latency sensitivity of any "stays on-prem" integration | [`01-discovery/inventories/07-application-inventory.md`](../01-discovery/inventories/07-application-inventory.md) |
| Budget constraint | [`00-project-overview/06-assumptions-and-constraints.md`](../00-project-overview/06-assumptions-and-constraints.md) constraint C6 |

## Decision matrix

| Requirement Level | Recommendation |
|---|---|
| Sustained bandwidth need under ~1-2 Gbps, latency-tolerant integrations only | **VPN** (Cloud VPN, HA VPN for redundancy) — faster to provision (days, not months), lower cost, sufficient for most incremental sync and integration traffic |
| Sustained bandwidth need above VPN's practical throughput ceiling, or latency-sensitive integrations (e.g., a real-time-ish OMS integration) | **Dedicated or Partner Interconnect** — higher throughput and lower, more consistent latency, but materially longer provisioning lead time |
| Uncertain / early in the program | Start with **HA VPN** to unblock early migration work immediately, while separately evaluating and, if needed, initiating Interconnect provisioning in parallel — do not block all connectivity on an Interconnect decision |

## Recommended approach for this migration

Given the ecommerce platform's described scale (moderate-to-large Hadoop
estate) and the phased, wave-based migration approach (not requiring full
bandwidth on day one), the recommended default is:

1. **Provision HA VPN first**, unblocking Foundation-phase and early-wave
   migration work immediately.
2. **Measure actual sustained bandwidth utilization** during the first few
   migration waves' parallel-run periods.
3. **If utilization approaches VPN's practical ceiling**, initiate
   Dedicated/Partner Interconnect provisioning at that point — with the
   lead time risk explicitly flagged to the Migration Program Lead given
   its impact on later wave scheduling.

This avoids the schedule risk of blocking all early work on Interconnect's
long lead time, while keeping the option open based on real, measured
need rather than upfront guesswork.

## HA VPN configuration

```hcl
# Terraform excerpt — see 13-infrastructure/
resource "google_compute_ha_vpn_gateway" "prod_vpn_gw" {
  name    = "prod-ha-vpn-gateway"
  network = google_compute_network.prod_vpc.id
  region  = var.region
}

resource "google_compute_external_vpn_gateway" "onprem_gw" {
  name            = "onprem-vpn-gateway"
  redundancy_type = "TWO_IPS_REDUNDANCY"
  interface {
    id         = 0
    ip_address = var.onprem_vpn_ip_primary
  }
  interface {
    id         = 1
    ip_address = var.onprem_vpn_ip_secondary
  }
}
# ... VPN tunnels and BGP session configuration per environment
```

HA VPN (not classic/single-tunnel VPN) is used for redundancy — a single
VPN tunnel is a connectivity single point of failure that directly
threatens the RPO/RTO targets established in
[`01-discovery/inventories/05-disaster-recovery-rpo-rto.md`](../01-discovery/inventories/05-disaster-recovery-rpo-rto.md)
for any Tier 1 domain relying on it for parallel-run sync.

## Common Mistakes

- Defaulting to Interconnect "to be safe" without confirming the actual
  bandwidth requirement first, incurring unnecessary cost and schedule
  delay for a requirement VPN would have met.
- Provisioning single-tunnel VPN instead of HA VPN, creating an avoidable
  connectivity single point of failure.

## Production Notes

If Interconnect is ultimately required for any Tier 1 domain's ongoing
production traffic (not just migration-period transfer), initiate that
provisioning request as early as possible in the program, independent of
when the specific wave needing it is scheduled — the lead time risk (R9)
means this decision cannot be made reactively.
