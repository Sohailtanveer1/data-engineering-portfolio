# Discovery Questions — Networking Team

**Purpose:** Understand current network topology, connectivity patterns,
and constraints so [`11-network/`](../../11-network/README.md) can design
GCP connectivity (VPN/Interconnect, DNS, firewall) that preserves required
integrations with systems staying on-prem, without becoming the long-pole
dependency for the whole program (see R9 in the risk register).
**Owner:** Migration Program Lead, conducted with Network Engineering lead.
**Audience:** Network engineering, and where applicable, the team owning
any existing cloud connectivity (if other GCP workloads already exist).

---

## Questions

| # | Question | Why we ask it |
|---|---|---|
| 1 | Does any GCP connectivity (VPN, Interconnect, existing landing zone) already exist for any other workload? | Reusing existing connectivity is far faster than provisioning new — directly affects the Foundation-phase timeline. |
| 2 | What is the current network topology around the Hadoop cluster — VLANs, subnets, firewall zones? | Baseline for designing equivalent-or-tighter GCP VPC/firewall segmentation in [`11-network/`](../../11-network/README.md). |
| 3 | Which on-prem systems must the GCP platform continue to reach after migration (ERP, POS, payment gateway, WMS, partner SFTP)? | Defines the persistent connectivity requirements that don't go away just because compute/storage moved to GCP. |
| 4 | What is the expected data volume and latency requirement for on-prem↔GCP connectivity during the parallel-run/transition period? | Sizes the VPN vs. Dedicated/Partner Interconnect decision — VPN may be insufficient for large parallel-run data volumes. |
| 5 | What is the current DNS setup, and are there internal hostnames the new platform needs to resolve (or be resolvable as)? | Avoids broken hardcoded hostnames surfacing mid-migration in scripts/configs discovered during [`02-dependency-analysis/`](../../02-dependency-analysis/README.md). |
| 6 | What firewall change process exists today, and what's the typical lead time for a new rule? | Long lead times must be built into the Foundation-phase timeline explicitly, not discovered when a rule request stalls a wave. |
| 7 | Are there any existing IP range conflicts we need to avoid when designing GCP VPC CIDR ranges? | On-prem RFC1918 ranges must not collide with GCP VPC ranges if VPN/Interconnect connectivity is used. |
| 8 | Is there an existing Cloud NAT / egress control policy elsewhere in the org we should align with? | Consistency avoids the new platform becoming a security exception that fails a later audit. |
| 9 | What is the process and lead time for provisioning a new Interconnect circuit, if required? | Interconnect provisioning can take months — this must be flagged as an early-critical-path item if required, not discovered late. |
| 10 | Are there existing network monitoring/logging tools (flow logs, IDS/IPS) that the GCP network design needs to integrate with? | Ensures the new platform doesn't create a network blind spot for existing security monitoring. |

## Validation of answers

Confirm CIDR ranges and firewall rules against actual router/firewall
configuration exports, not verbal description, before finalizing VPC design
in [`11-network/`](../../11-network/README.md).
