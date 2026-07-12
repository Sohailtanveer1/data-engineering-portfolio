# Private Connectivity, Cloud NAT & Private Google Access

**Purpose:** Configure private-by-default connectivity for Dataproc and
Composer resources — no public IPs, egress only via controlled paths —
per the target architecture's design principle.
**Owner:** Network Engineering.

---

## Private Google Access

Enabled on every subnet hosting Dataproc/Composer resources, allowing
private-IP-only VMs to reach Google APIs (GCS, BigQuery, Secret Manager,
Artifact Registry) without traversing the public internet or requiring a
public IP:

```hcl
# Terraform excerpt — see 13-infrastructure/
resource "google_compute_subnetwork" "dataproc_subnet" {
  name                     = "dataproc-subnet"
  private_ip_google_access = true
  # ...
}
```

This is what allows a Dataproc cluster with no public IP to still read/
write GCS and BigQuery — a core requirement given the no-public-IP
firewall policy in
[`02-firewall-rules.md`](02-firewall-rules.md).

## Cloud NAT

For the narrower set of cases requiring genuine public internet egress
(installing a public PyPI/Maven package during cluster initialization,
calling a third-party SaaS API per
[`01-discovery/inventories/12-external-dependencies.md`](../01-discovery/inventories/12-external-dependencies.md)),
Cloud NAT provides outbound-only internet access without any inbound
public exposure:

```hcl
resource "google_compute_router_nat" "prod_nat" {
  name                               = "prod-nat"
  router                             = google_compute_router.prod_router.name
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "LIST_OF_SUBNETWORKS"
  subnetwork {
    name                    = google_compute_subnetwork.dataproc_subnet.id
    source_ip_ranges_to_nat = ["ALL_IP_RANGES"]
  }
}
```

## NAT sizing and logging

- **Log NAT connections** (`enable_logging = true`) for the audit trail
  benefit and for troubleshooting connectivity issues — this is
  particularly useful during migration when new external dependencies are
  being validated.
- **Size NAT IP allocation** to handle peak concurrent Dataproc worker
  count under autoscaling — insufficient NAT IP/port allocation under load
  causes silent connection failures that are hard to diagnose without
  NAT logging already enabled.

## Common Mistakes

- Assigning public IPs to Dataproc workers as a quick fix when a package
  install fails during cluster initialization, instead of diagnosing why
  Cloud NAT egress isn't working — this silently reintroduces public
  exposure that the firewall/Org Policy design is meant to prevent.
- Under-sizing Cloud NAT for peak autoscaled worker count, causing
  intermittent, hard-to-diagnose egress failures specifically during high
  scale-out periods (i.e., exactly when a Tier 1 job is under the most
  load).

## Production Notes

Enable NAT logging in `prod` from day one, not added reactively after a
connectivity issue — the logging itself has minimal cost and provides
essential troubleshooting data exactly when it's needed most.
