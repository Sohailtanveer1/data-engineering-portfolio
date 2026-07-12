# DNS Design

**Purpose:** Ensure internal hostname resolution works correctly across
the hybrid on-prem/GCP environment, addressing
[`01-discovery/questions/04-networking-team.md`](../01-discovery/questions/04-networking-team.md)
Q5.
**Owner:** Network Engineering.

---

## DNS requirements

| Requirement | Solution |
|---|---|
| GCP resources resolving on-prem internal hostnames (e.g., the OMS database host) | Cloud DNS **forwarding zone** pointing at the on-prem DNS server(s), reachable over the hybrid connectivity path |
| On-prem systems resolving GCP-side hostnames (e.g., if any on-prem system needs to reach a GCP-hosted endpoint by name) | Cloud DNS **peering zone**, or a forwarding rule configured on the on-prem DNS server pointing at Cloud DNS |
| Internal GCP service-to-service resolution (Dataproc cluster nodes, Composer) | Handled automatically by GCP's internal DNS — no custom configuration needed |

## Hardcoded hostname remediation

Per the hardcoded-value findings in
[`02-dependency-analysis/`](../02-dependency-analysis/README.md), any job
or script with a hardcoded on-prem IP address instead of a resolvable
hostname is a specific migration risk — IP addresses are far more likely
to change or become unreachable than a stable, resolvable hostname. Flag
and remediate any hardcoded IP found during
[`07-spark-migration/`](../07-spark-migration/README.md) configuration
externalization work as a related fix, replacing it with a hostname
resolved via the DNS design in this document.

## Configuration

```hcl
# Terraform excerpt — see 13-infrastructure/
resource "google_dns_managed_zone" "onprem_forwarding" {
  name        = "onprem-forwarding-zone"
  dns_name    = "internal.company.com."
  visibility  = "private"

  forwarding_config {
    target_name_servers {
      ipv4_address = "10.0.1.53"  # on-prem DNS server, reachable via VPN/Interconnect
    }
  }

  private_visibility_config {
    networks {
      network_url = google_compute_network.prod_vpc.id
    }
  }
}
```

## Validation

Before any job depending on an on-prem hostname is migrated, validate DNS
resolution explicitly from within a test Dataproc cluster (`nslookup
<on-prem-hostname>` from a cluster node) — do not assume the forwarding
zone configuration works correctly without this direct confirmation.

## Common Mistakes

- Assuming DNS forwarding "just works" once configured without testing
  resolution from an actual GCP compute resource, not just validating the
  Terraform applied successfully.
- Missing a specific internal domain suffix used on-prem that isn't
  covered by the configured forwarding zone's `dns_name` pattern.

## Production Notes

Test DNS resolution for every on-prem hostname referenced by a Tier 1
job's configuration explicitly, as part of that job's
[`10-integration-testing-strategy.md`](../07-spark-migration/10-integration-testing-strategy.md)
integration test suite — a DNS resolution failure discovered only at
cutover is an entirely avoidable, easily-tested-for risk.
