# VPC & Subnet Design

**Purpose:** Define the VPC and subnet layout per environment, sized to
avoid CIDR conflicts with on-prem address space per
[`01-discovery/questions/04-networking-team.md`](../01-discovery/questions/04-networking-team.md)
Q7.
**Owner:** Network Engineering.

---

## VPC-per-environment model

One VPC per GCP project/environment (dev/qa/stage/prod), consistent with
the full environment isolation constraint (C4) established in
[`04-target-architecture/02-landing-zone-and-project-structure.md`](../04-target-architecture/02-landing-zone-and-project-structure.md)
— not a single shared VPC across environments with subnet-based isolation.

## CIDR allocation

| Environment | VPC CIDR | Notes |
|---|---|---|
| `dev` | `10.10.0.0/20` | Confirm no overlap with on-prem RFC1918 ranges |
| `qa` | `10.11.0.0/20` | |
| `stage` | `10.12.0.0/20` | |
| `prod` | `10.20.0.0/16` | Larger allocation for production headroom (autoscaled Dataproc worker IP consumption) |

**These ranges are illustrative placeholders** — the actual allocation
must be confirmed against the real on-prem CIDR ranges collected via
[`01-discovery/questions/04-networking-team.md`](../01-discovery/questions/04-networking-team.md)
Q7 before being finalized, to guarantee zero overlap.

## Subnet design (per environment VPC)

| Subnet | Purpose | CIDR (within `prod` example) |
|---|---|---|
| `dataproc-subnet` | Dataproc cluster nodes (private IP only) | `10.20.0.0/20` |
| `composer-subnet` | Cloud Composer environment | `10.20.16.0/22` |
| `connectivity-subnet` | VPN/Interconnect gateway resources | `10.20.20.0/28` |

Subnets are regional, aligned to the primary region selected in
[`04-target-architecture/04-storage-architecture.md`](../04-target-architecture/04-storage-architecture.md)
regional strategy — a secondary region's subnet is added only if the DR
design in
[`01-discovery/inventories/05-disaster-recovery-rpo-rto.md`](../01-discovery/inventories/05-disaster-recovery-rpo-rto.md)
requires multi-region compute, not by default.

## Sizing for Dataproc autoscaling headroom

Subnet sizing for `dataproc-subnet` must account for the **peak** worker
node count under autoscaling (per
[`12-cluster-design/`](../12-cluster-design/README.md)), not the steady-
state count — running out of available IPs mid-autoscale-up during a peak
trading event would be a self-inflicted, entirely avoidable capacity
incident.

## Common Mistakes

- Sizing subnets for today's known workload without headroom for
  autoscaling growth, causing IP exhaustion exactly when it matters most
  (during a scale-up event).
- Allocating CIDR ranges without cross-checking on-prem address space,
  discovered only when VPN/Interconnect connectivity is attempted and
  routing conflicts surface.

## Production Notes

Confirm the `prod` VPC's CIDR allocation with Network Engineering against
the full on-prem range **and** any other existing GCP workloads' VPC
ranges in the same organization, if any exist — a conflict with another
internal GCP project is just as disruptive as an on-prem conflict.
