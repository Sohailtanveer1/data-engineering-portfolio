# Routes & Peering

**Purpose:** Define routing configuration ensuring traffic between GCP,
on-prem, and Google APIs flows through the correct, intended paths.
**Owner:** Network Engineering.

---

## Route types in use

| Route Type | Purpose |
|---|---|
| System-generated subnet routes | Automatic, internal-to-VPC traffic — no manual configuration needed |
| Custom routes to on-prem CIDR ranges | Routes traffic destined for on-prem systems through the VPN/Interconnect gateway, dynamically via BGP (HA VPN) or statically if required |
| Private Google Access routes | Automatic once Private Google Access is enabled per subnet (per [`03-private-connectivity-and-nat.md`](03-private-connectivity-and-nat.md)) |
| Default route to Cloud NAT | For general internet egress not covered by a more specific route |

## BGP configuration (HA VPN)

HA VPN uses BGP for dynamic route exchange with the on-prem VPN gateway,
avoiding the need for manually maintained static routes that can drift
out of sync as on-prem network topology evolves:

```hcl
resource "google_compute_router" "prod_router" {
  name    = "prod-router"
  network = google_compute_network.prod_vpc.id
  region  = var.region
  bgp {
    asn = 65001  # GCP-side ASN, coordinated with on-prem network team's ASN choice
  }
}
```

Coordinate ASN selection and BGP session parameters directly with Network
Engineering's on-prem routing configuration — this is not a purely
GCP-side decision.

## VPC Peering (if applicable)

If other GCP projects/VPCs in the organization need direct connectivity to
the data platform VPC (e.g., a shared services project), use VPC Peering
or Shared VPC per the org's broader GCP landing zone design — evaluate
this against
[`04-target-architecture/02-landing-zone-and-project-structure.md`](../04-target-architecture/02-landing-zone-and-project-structure.md)
assumption A1 (whether a broader landing zone already exists) before
designing this in isolation.

## Common Mistakes

- Configuring static routes to on-prem instead of using BGP with HA VPN,
  creating a maintenance burden every time on-prem network topology
  changes (new subnets, re-IP events) that BGP would have propagated
  automatically.
- Failing to coordinate BGP ASN/session parameters with the on-prem
  network team, causing a session establishment failure discovered only
  during connectivity testing rather than design review.

## Production Notes

Validate route propagation explicitly (not just BGP session establishment)
by testing actual reachability to every on-prem system in
[`01-discovery/inventories/07-application-inventory.md`](../01-discovery/inventories/07-application-inventory.md)
from a GCP test resource — a successfully established BGP session does not
guarantee every expected route is actually being advertised and accepted
correctly.
