# Configuration Baseline

**Purpose:** A single, version-pinned snapshot of every relevant
configuration file across the platform, captured at a known point in time,
so that (a) target architecture design has an authoritative reference and
(b) any configuration drift during the migration program itself is
detectable by diffing against this baseline.
**Owner:** Platform Engineering.
**Inputs:** Direct export of every listed configuration file.
**Outputs:** The reference baseline cited by every other document in this
folder and by [`04-target-architecture/`](../04-target-architecture/README.md).
**Validation method:** Store actual exported config files (not just
transcribed values) in a version-controlled location alongside this
document — this markdown file is the index and summary, not the sole
record.

---

## Baseline snapshot metadata

| Field | Value |
|---|---|
| Snapshot captured by | _(name)_ |
| Snapshot date | _(date)_ |
| Cluster state at capture (normal / degraded / maintenance) | _(fill in — capture during normal operation)_ |
| Config files archived at | _(path/location — e.g., `03-current-environment/config-snapshots/<date>/`)_ |

## Configuration file index

| File | Component | Key Settings Summarized Elsewhere In This Folder | Archived Copy Location |
|---|---|---|---|
| `core-site.xml` | Hadoop Core | Security (06), Storage (05) | |
| `hdfs-site.xml` | HDFS | Cluster topology (01) | |
| `yarn-site.xml` | YARN | Resource assessment (02) | |
| `capacity-scheduler.xml` / `fair-scheduler.xml` | YARN Scheduler | Queue configuration (02) | |
| `hive-site.xml` | Hive | Hive environment (04) | |
| `spark-defaults.conf` | Spark | Spark environment (03) | |
| `spark-env.sh` | Spark | Spark environment (03) | |
| `ranger-*-policies.json` (exported) | Ranger | Security assessment (06) | |
| `krb5.conf` | Kerberos | Security assessment (06) | |
| Oozie `oozie-site.xml` | Oozie | Scheduler inventory ([`01-discovery/inventories/10-scheduler-inventory.md`](../01-discovery/inventories/10-scheduler-inventory.md)) | |

## Version matrix (all components, one table)

| Component | Version | Distribution | End-of-Support Date |
|---|---|---|---|
| Hadoop/HDFS | | | |
| YARN | | | |
| Spark | | | |
| Hive | | | |
| Oozie (if applicable) | | | |
| Zookeeper | | | |
| Ranger (if applicable) | | | |
| OS | | | |
| JDK | | | |

Any component past end-of-support is flagged as an independent migration
urgency driver, separate from the strategic motivations in the executive
summary — running unsupported infrastructure is itself a risk regardless of
the migration timeline.

## How this baseline is used downstream

- [`04-target-architecture/`](../04-target-architecture/README.md) designs
  the target state as an explicit, reasoned departure from this baseline —
  every deviation should be traceable back to a specific limitation or
  pain point recorded in this folder.
- [`07-spark-migration/`](../07-spark-migration/README.md) uses the Spark/
  Scala version matrix directly to scope API compatibility work.
- Configuration drift during the (likely months-long) migration program is
  detected by periodically re-exporting these files and diffing against
  this baseline — material drift should be flagged to the Migration
  Program Lead, since it may invalidate assumptions made earlier in the
  program.

## Common Mistakes

- Capturing configuration values by asking the platform team to describe
  them from memory instead of exporting the actual files — memory is
  frequently out of date even for engineers who work with the system daily.
- Not archiving the raw files themselves, only summarized values — raw
  files are needed later for detailed comparison work in
  [`04-target-architecture/`](../04-target-architecture/README.md) and
  [`13-infrastructure/`](../13-infrastructure/README.md).

## Production Notes

Re-capture this baseline once more immediately before
[`04-target-architecture/`](../04-target-architecture/README.md) design
work formally begins, if more than 4–6 weeks have elapsed since the
initial capture — configuration in an actively-used production platform
does not stay static.
