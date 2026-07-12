# Hadoop Cluster Assessment

**Purpose:** Document the physical and logical topology of the current
Hadoop cluster — node counts, roles, hardware specs, and HDFS
configuration — as the factual baseline for capacity comparison against
target Dataproc sizing in
[`12-cluster-design/`](../12-cluster-design/README.md).
**Owner:** Platform Engineering.
**Inputs:** `hdfs dfsadmin -report`, cluster inventory/asset management
system, `core-site.xml`, `hdfs-site.xml`.
**Outputs:** Feeds [`12-cluster-design/`](../12-cluster-design/README.md)
sizing and [`19-cost-optimization/`](../19-cost-optimization/README.md)
cost baseline comparison.
**Validation method:** Cross-check node count and role assignment against
`hdfs dfsadmin -report` and YARN Resource Manager's active node list —
these are ground truth, not the asset inventory system (which can lag
reality).

---

## Cluster topology

| Role | Node Count | CPU per Node | RAM per Node | Local Disk per Node | Disk Type | OS Version |
|---|---|---|---|---|---|---|
| Master (NameNode, active) | 1 | _(fill in)_ | _(fill in)_ | _(fill in)_ | _(HDD/SSD)_ | _(fill in)_ |
| Master (NameNode, standby) | 1 | _(fill in)_ | _(fill in)_ | _(fill in)_ | _(HDD/SSD)_ | _(fill in)_ |
| Master (YARN ResourceManager) | 1–2 (HA) | _(fill in)_ | _(fill in)_ | _(fill in)_ | _(HDD/SSD)_ | _(fill in)_ |
| Master (Hive Metastore host) | 1–2 | _(fill in)_ | _(fill in)_ | _(fill in)_ | _(HDD/SSD)_ | _(fill in)_ |
| Worker (DataNode + NodeManager) | _(fill in)_ | _(fill in)_ | _(fill in)_ | _(fill in)_ | _(HDD/SSD)_ | _(fill in)_ |
| Edge/Gateway nodes | _(fill in)_ | _(fill in)_ | _(fill in)_ | _(fill in)_ | _(HDD/SSD)_ | _(fill in)_ |

**Total cluster footprint:** _(total cores)_ cores / _(total RAM)_ / _(total
raw disk)_ across _(N)_ nodes.

## HDFS configuration

| Setting | Current Value | Notes |
|---|---|---|
| Replication factor | _(typically 3)_ | Drives effective-vs-raw capacity calc in [`01-discovery/inventories/11-storage-inventory.md`](../01-discovery/inventories/11-storage-inventory.md) |
| Block size | _(e.g., 128 MB)_ | Affects small-file behavior; relevant to GCS object sizing strategy |
| NameNode HA configuration | _(Active/Standby via QJM, or single NameNode)_ | Single NameNode = current single point of failure, relevant to DR gap analysis |
| Federation in use? | _(yes/no)_ | If yes, document namespace split |
| Rack awareness configured? | _(yes/no)_ | |
| Erasure coding in use? | _(yes/no, which policy)_ | Affects effective capacity calculation if used for cold data |

## Hadoop distribution and version

| Component | Distribution (Cloudera/Hortonworks/Apache/other) | Version | End-of-support date (if known) |
|---|---|---|---|
| Hadoop Core | | | |
| HDFS | | | |
| YARN | | | |

Flag explicitly if the current distribution/version is at or past its
vendor end-of-support date — this is an independent urgency driver for the
migration, separate from the cost/agility motivations in the executive
summary.

## Cluster age and hardware lifecycle

| Node Role | Hardware Purchase/Deploy Date | Expected Refresh Date | Currently Past Refresh? |
|---|---|---|---|
| Worker nodes (oldest batch) | | | |
| Worker nodes (newest batch) | | | |
| Master nodes | | | |

Hardware nearing or past its refresh date independently supports the case
for migration urgency (see risk R-hardware in
[`00-project-overview/07-risk-register-summary.md`](../00-project-overview/07-risk-register-summary.md)
— add if not already present) and should be cross-checked against
[`01-discovery/questions/02-platform-team.md`](../01-discovery/questions/02-platform-team.md)
Q8.

## Common Mistakes

- Recording node counts from an org chart or budget document instead of
  the live cluster's own reporting tools.
- Omitting edge/gateway nodes from the topology — they don't run HDFS/YARN
  daemons but are critical to the dependency analysis in
  [`02-dependency-analysis/`](../02-dependency-analysis/README.md) since
  cron and shell scripts commonly run there.

## Production Notes

Document exactly which nodes (if any) are dedicated to specific business
functions (e.g., a queue or node pool reserved for fraud-detection jobs) —
this constraint, if it exists, needs an explicit equivalent (or explicit
justified removal) in [`12-cluster-design/`](../12-cluster-design/README.md).
