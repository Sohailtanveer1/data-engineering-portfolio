# 11 — Network Configuration

## Purpose

Implement the connectivity design principles from
[`04-target-architecture/08-network-architecture-overview.md`](../04-target-architecture/08-network-architecture-overview.md)
as concrete VPC, firewall, DNS, and hybrid-connectivity configuration —
ensuring every "stays on-prem" system in
[`01-discovery/inventories/07-application-inventory.md`](../01-discovery/inventories/07-application-inventory.md)
remains reachable, while keeping GCP compute resources private by default.

## Owner

**Network Engineering**, reviewed by Security Engineering.

## Inputs

- Network architecture overview from
  [`04-target-architecture/08-network-architecture-overview.md`](../04-target-architecture/08-network-architecture-overview.md).
- Current network topology from
  [`03-current-environment/05-storage-and-network-assessment.md`](../03-current-environment/05-storage-and-network-assessment.md).
- Networking team interview findings from
  [`01-discovery/questions/04-networking-team.md`](../01-discovery/questions/04-networking-team.md).

## Outputs

- Provisioned VPC, subnets, firewall rules, DNS configuration.
- A resolved connectivity method (VPN vs. Interconnect) decision, per the
  open item O1 in
  [`04-target-architecture/09-architecture-decision-log.md`](../04-target-architecture/09-architecture-decision-log.md).
- Confirmed, tested reachability to every required on-prem system.

## Prerequisites

[`04-target-architecture/`](../04-target-architecture/README.md) gated;
[`10-security/`](../10-security/README.md) substantially complete (network
and security design are interdependent, per the target architecture's
design principles).

## Deliverables

1. VPC and subnet design.
2. Firewall rule set.
3. Private connectivity and Cloud NAT configuration.
4. DNS design.
5. Hybrid connectivity (VPN/Interconnect) implementation.
6. Routes and peering configuration.
7. Execution checklist.

## Risks

Interconnect provisioning lead time (potentially months) is the most
significant schedule risk in this folder — see risk R9 in
[`00-project-overview/07-risk-register-summary.md`](../00-project-overview/07-risk-register-summary.md).
This folder's connectivity decision should be finalized and, if
Interconnect is required, provisioning initiated as early as possible.

## Rollback

Network configuration changes are provisioned via Terraform and reversible
via standard Terraform state management — see
[`13-infrastructure/`](../13-infrastructure/README.md). Hybrid
connectivity changes (VPN/Interconnect) require more careful rollback
planning given potential impact to any already-migrated traffic depending
on them.

## Validation

Every "stays on-prem" system from
[`01-discovery/inventories/07-application-inventory.md`](../01-discovery/inventories/07-application-inventory.md)
must be confirmed reachable from the relevant GCP environment before that
environment is used for any production data migration.

## Best Practices

Finalize the VPN vs. Interconnect decision using actual measured transfer
volume requirements (per
[`04-target-architecture/08-network-architecture-overview.md`](../04-target-architecture/08-network-architecture-overview.md)),
not a default assumption — and initiate any required Interconnect
provisioning immediately once decided, given the lead time risk.

## Lessons Learned

CIDR range conflicts between on-prem and GCP VPC space, if not caught
early, force a costly VPC re-IP later — confirm this explicitly before any
non-trivial connectivity work begins.

## Common Mistakes

- Deferring the connectivity method decision until late in the program,
  discovering an Interconnect requirement only when parallel-run bandwidth
  needs are already pressing.
- Configuring firewall rules broadly ("allow all internal traffic") for
  expediency during initial setup and never tightening them before
  production.

## Production Notes

Validate hybrid connectivity bandwidth and latency against real,
production-representative transfer volumes (from
[`01-discovery/inventories/11-storage-inventory.md`](../01-discovery/inventories/11-storage-inventory.md))
well before any Tier 1 data domain's parallel-run period begins.

---

## Folder structure

```
11-network/
├── README.md                                        This file
├── 01-vpc-and-subnet-design.md                       VPC, subnets per environment
├── 02-firewall-rules.md                              Firewall rule set
├── 03-private-connectivity-and-nat.md                Private IP, Cloud NAT, Private Google Access
├── 04-dns-design.md                                  Internal DNS resolution
├── 05-hybrid-connectivity-vpn-interconnect.md        VPN/Interconnect decision and implementation
├── 06-routes-and-peering.md                          Routing configuration
└── 07-execution-checklist.md                          Per-environment execution checklist
```
