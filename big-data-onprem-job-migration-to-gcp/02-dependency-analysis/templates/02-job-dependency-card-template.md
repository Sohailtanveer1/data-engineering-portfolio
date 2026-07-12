# Template — Per-Job Dependency Card

**Purpose:** One completed card per Job ID, consolidating findings from
every applicable methodology document in [`../methodology/`](../methodology/)
into a single reference used during
[`14-job-migration/`](../../14-job-migration/README.md) wave planning and
[`07-spark-migration/`](../../07-spark-migration/README.md) execution.
**Owner:** Whoever performs dependency analysis for this job.
**When to use:** One card per job, filed alongside or linked from
[`01-discovery/inventories/06-job-inventory.md`](../../01-discovery/inventories/06-job-inventory.md).

---

## Job Dependency Card — `<JOB-ID>`

**Job Name:** `<job name>`
**Type:** `<Spark / Hive / Shell / Sqoop / Other>`
**Criticality Tier:** `<Tier 1-4, per business-critical-jobs inventory>`
**Card completed by:** `<name>` **Date:** `<date>` **Last refreshed:** `<date>`

### Upstream dependencies (what this job needs to run)

| Category | Detail | Source (table/path/system) | Confirmed via | Owner (if external) |
|---|---|---|---|---|
| Data input | | | | |
| Config/environment | | | | |
| Shared library/JAR | | | | |
| External system (DB/API/Kafka/SFTP/NFS) | | | | |

### Downstream consumers (what depends on this job's output)

| Consumer | Type (job/BI/partner/ad-hoc) | Criticality of consumer | Confirmed via |
|---|---|---|---|
| | | | |

### Scheduler / workflow context

- **Triggered by:** `<time-based / data-availability / manual>`
- **Upstream job(s) this depends on in the workflow graph:** `<list>`
- **Downstream job(s) that depend on this in the workflow graph:** `<list>`
- **Conditional/branching logic present?** `<yes/no — describe if yes>`

### Technical debt / risk flags

- [ ] Hardcoded paths/hostnames/credentials found (list below)
- [ ] Uses deprecated Spark/Hive APIs
- [ ] Not confirmed idempotent
- [ ] No automated retry/alerting today
- [ ] Depends on NFS mount
- [ ] Depends on a shared library also used by other jobs (list which)
- [ ] Owner unconfirmed / tribal knowledge risk

**Details on flagged items:**

_(free text)_

### Validation status

- [ ] Confirmed via at least one independent technique
- [ ] Confirmed via at least two independent techniques (required for Tier 1/2)
- [ ] Reviewed with job owner/developer
- [ ] Reviewed with downstream consumer(s)

### Migration readiness note

_(One-line summary for wave planning: is this job ready to be scheduled, or
what's blocking it? E.g., "Blocked — owner unconfirmed for
`legacy_vendor_feed_2019` upstream dependency, needs resolution before
wave assignment.")_
