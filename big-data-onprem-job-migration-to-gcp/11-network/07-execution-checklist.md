# Network Execution Checklist (Per Environment)

**Purpose:** A single checklist confirming network configuration is
complete and validated before an environment is used for any data
migration activity.
**Owner:** Network Engineering (executor).

---

## Checklist — Environment: `_______________`

### VPC & Subnets

- [ ] VPC and subnets provisioned per
      [`01-vpc-and-subnet-design.md`](01-vpc-and-subnet-design.md)
- [ ] CIDR ranges confirmed non-conflicting with on-prem and other GCP
      VPCs
- [ ] Subnets sized for peak autoscaling headroom

### Firewall

- [ ] Firewall rules applied per
      [`02-firewall-rules.md`](02-firewall-rules.md), default-deny posture
      confirmed
- [ ] No public IPs enabled on Dataproc/Composer resources (Org Policy
      confirmed active)
- [ ] No temporary/broad rules remaining from initial setup

### Private Connectivity

- [ ] Private Google Access enabled per
      [`03-private-connectivity-and-nat.md`](03-private-connectivity-and-nat.md)
- [ ] Cloud NAT provisioned and sized for peak concurrent worker count
- [ ] NAT logging enabled

### DNS

- [ ] On-prem forwarding zone configured per
      [`04-dns-design.md`](04-dns-design.md)
- [ ] Resolution validated from an actual GCP compute resource for every
      required on-prem hostname

### Hybrid Connectivity

- [ ] Connectivity method (VPN/Interconnect) decided per
      [`05-hybrid-connectivity-vpn-interconnect.md`](05-hybrid-connectivity-vpn-interconnect.md)
- [ ] HA VPN (or Interconnect) provisioned and tunnels/circuits active
- [ ] BGP sessions established and routes confirmed propagating correctly
      per [`06-routes-and-peering.md`](06-routes-and-peering.md)

### Validation

- [ ] Every on-prem system in
      [`01-discovery/inventories/07-application-inventory.md`](../01-discovery/inventories/07-application-inventory.md)
      confirmed reachable from this environment
- [ ] Bandwidth/latency validated against real transfer volume
      requirements for Tier 1 domains (prod only)

### Sign-off

- [ ] Reviewed by Network Engineering
- [ ] Reviewed by Security Engineering
- [ ] Recorded complete in
      [`14-job-migration/`](../14-job-migration/README.md) tracker as a
      gate passed for this environment

**Executed by:** ________________ **Date:** ________________
**Reviewed by:** ________________ **Date:** ________________

## Common Mistakes

- Marking connectivity "done" once a VPN tunnel shows as UP without
  validating actual application-level reachability to every required
  on-prem system — a tunnel being up is necessary but not sufficient.
