# Migration Strategy Overview — DistCp vs. Storage Transfer Service

**Purpose:** Provide an explicit, per-data-domain decision framework for
which transfer mechanism to use, rather than defaulting to one tool for
the entire platform.
**Owner:** Platform Engineering.
**Inputs:** [`01-discovery/inventories/11-storage-inventory.md`](../01-discovery/inventories/11-storage-inventory.md)
(volume per domain), [`11-network/`](../11-network/README.md) (available
bandwidth/connectivity method).

---

## Tool comparison

| Factor | Hadoop DistCp (with GCS connector) | Storage Transfer Service (STS) |
|---|---|---|
| Runs from | On-prem cluster (as a MapReduce/Spark job) | Fully managed GCP service, agent-based or agentless |
| Best for | Large volumes with available on-prem compute capacity and direct network path to GCS | Large volumes where minimizing on-prem cluster load matters, or where a managed, resumable, schedulable transfer is preferred |
| Bandwidth control | Manual (via MapReduce job tuning, network QoS) | Built-in scheduling and rate limiting |
| Incremental sync support | Yes, via `-update` flag (timestamp/size-based) | Yes, native scheduled incremental sync with delete-on-source-removal options |
| Consumes on-prem cluster resources | Yes — runs as a job on the Hadoop cluster, competing with production workloads unless carefully scheduled | Minimal — agent-based STS uses lightweight on-prem agents, not full cluster jobs |
| Operational complexity | Lower initial complexity (familiar tool for Hadoop admins) | Slightly higher initial setup (agent pool deployment) but lower ongoing operational burden |
| Checksum validation | Manual, via separate checksum comparison (see [`05-checksum-and-validation.md`](05-checksum-and-validation.md)) | Built-in integrity verification, still supplemented by the same manual checksum procedure for a second independent check |

## Decision framework per data domain

| Data Domain Characteristic | Recommended Tool |
|---|---|
| Very large (multi-TB+), one-time historical bulk load, on-prem cluster has spare off-peak capacity | DistCp |
| Ongoing/repeated incremental sync needed throughout an extended parallel-run period | Storage Transfer Service (agent-based) — better suited to scheduled, managed, repeated syncs |
| Small-to-medium domain, simplicity preferred, low risk tolerance for new tooling | DistCp (most Hadoop admins already know it) |
| On-prem cluster is resource-constrained and cannot spare capacity for a transfer job | Storage Transfer Service (agent-based) — offloads transfer execution from the Hadoop cluster itself |

## Recommended default for this migration

Given the described platform (ecommerce, capacity-constrained cluster —
see pain point #1 in
[`03-current-environment/09-pain-points-and-bottlenecks.md`](../03-current-environment/09-pain-points-and-bottlenecks.md)),
the default recommendation is:

- **Initial bulk historical load:** DistCp, scheduled during the
  lowest-utilization windows from
  [`01-discovery/inventories/03-peak-hours-and-downtime-windows.md`](../01-discovery/inventories/03-peak-hours-and-downtime-windows.md),
  since it's a one-time event where a temporary resource cost is
  acceptable.
- **Ongoing incremental sync during parallel-run:** Storage Transfer
  Service (agent-based), since it doesn't compete with production
  workloads for cluster capacity over an extended period and provides
  built-in scheduling/monitoring — see
  [`04-incremental-sync-strategy.md`](04-incremental-sync-strategy.md).

This is a default, not a mandate — confirm per data domain against the
framework above, and record the actual decision in the per-domain
execution checklist ([`08-migration-execution-checklist.md`](08-migration-execution-checklist.md)).

## Per-domain migration plan table

| Data Domain (from storage inventory) | Volume (effective) | Chosen Tool (Bulk) | Chosen Tool (Incremental) | Target Wave | Rationale |
|---|---|---|---|---|---|
| `/data/pricing/` | 12 TB | DistCp | STS | Early wave (Tier 1, but well-understood) | Moderate volume, off-peak capacity available |
| `/data/fraud/` | 18 TB | DistCp | STS (frequent sync — hourly job) | Later wave (Tier 1, high sensitivity) | Larger volume, needs tight incremental sync given hourly job cadence |
| `/data/clickstream/` | 45 TB | STS (agent-based, minimizes cluster load given large volume) | STS | Mid wave (Tier 3, lower risk) | Largest volume — avoid tying up cluster capacity for an extended DistCp run |

_(Illustrative — populate from the actual storage inventory.)_

## Common Mistakes

- Choosing DistCp by default for every domain without checking whether the
  on-prem cluster actually has spare capacity to run it without impacting
  production jobs — this can silently reproduce pain point #1 from
  [`03-current-environment/`](../03-current-environment/README.md) during
  the migration itself.
- Not planning the incremental-sync tool choice separately from the
  bulk-load tool choice — they optimize for different things and don't
  have to be the same tool.

## Production Notes

For Tier 1 data domains, run a **volume and timing dry run** (measuring
actual observed transfer throughput on a small sample) before committing to
a wave schedule — theoretical bandwidth calculations routinely overstate
real-world throughput once contention, retries, and small-file overhead are
accounted for.
