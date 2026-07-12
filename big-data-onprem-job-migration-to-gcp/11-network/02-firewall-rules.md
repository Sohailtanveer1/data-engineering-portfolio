# Firewall Rules

**Purpose:** Define a default-deny, explicitly-allowed firewall rule set —
matching or exceeding the segmentation documented in
[`03-current-environment/05-storage-and-network-assessment.md`](../03-current-environment/05-storage-and-network-assessment.md).
**Owner:** Network Engineering, reviewed by Security Engineering.

---

## Default posture: deny-all, explicit allow

Every VPC starts with GCP's implied deny-all for ingress (no rule needed —
this is default) and an explicit, minimal set of allow rules — never a
broad "allow all internal traffic" rule for convenience.

## Core firewall rules

| Rule | Direction | Source | Destination | Ports | Purpose |
|---|---|---|---|---|---|
| `allow-dataproc-internal` | Ingress | `dataproc-subnet` (self) | `dataproc-subnet` | All (cluster-internal Spark/YARN communication) | Required for Dataproc cluster nodes to communicate with each other |
| `allow-composer-to-dataproc` | Ingress | `composer-subnet` | `dataproc-subnet` | 443 (Dataproc API, not direct node access) | Composer submits jobs via the Dataproc API, not direct node connections |
| `allow-iap-ssh` | Ingress | Identity-Aware Proxy range (`35.235.240.0/20`) | All subnets | 22 | SSH access only via IAP tunnel, never a public IP — no direct SSH exposure |
| `allow-health-checks` | Ingress | GCP health check ranges | Relevant subnets | Per service | Required for any internal load balancer health checks |
| `deny-all-other-ingress` | Ingress | `0.0.0.0/0` | All | All | Explicit lowest-priority deny, defense in depth beyond GCP's implicit default |

## Egress rules

| Rule | Destination | Purpose |
|---|---|---|
| `allow-egress-google-apis` | Google API ranges (via Private Google Access) | GCS/BigQuery/Secret Manager access without public internet transit |
| `allow-egress-nat` | Via Cloud NAT | Package installs, external API calls (per [`03-private-connectivity-and-nat.md`](03-private-connectivity-and-nat.md)) |
| `allow-egress-onprem` | On-prem CIDR range, via VPN/Interconnect | Required connectivity to systems per [`01-discovery/inventories/07-application-inventory.md`](../01-discovery/inventories/07-application-inventory.md) |
| `deny-all-other-egress` | `0.0.0.0/0` | Explicit lowest-priority deny |

## No public IPs on Dataproc/Composer

Per the target architecture's private-by-default principle
([`04-target-architecture/08-network-architecture-overview.md`](../04-target-architecture/08-network-architecture-overview.md)),
Dataproc cluster nodes and Composer environment resources have **no public
IP addresses** — enforced via an Org Policy constraint
(`compute.vmExternalIpAccess`) in addition to the firewall rules above, as
defense in depth.

## Common Mistakes

- Creating a broad "allow internal" rule (e.g., allow all traffic from
  `10.0.0.0/8`) early in setup "to unblock testing" and forgetting to
  narrow it before production — track every temporary broad rule
  explicitly with a removal date, don't rely on memory.
- Allowing direct SSH access via public IP for debugging convenience,
  bypassing the IAP tunnel requirement.

## Production Notes

Run a firewall rule audit before every production cutover wave, confirming
no temporary/broad rules remain active from earlier development or testing
work — this should be a standing item in the
[`21-cutover/`](../21-cutover/README.md) pre-cutover checklist.
