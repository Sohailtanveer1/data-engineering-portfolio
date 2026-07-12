# Downstream Consumer Analysis

**Purpose:** Every methodology document so far in this folder focuses on
what a job *depends on* (upstream). This document flips the direction:
for every job and every table, who depends on *it*. This is the analysis
most often skipped, and it is the category most likely to cause a
"surprise" production incident, because the team migrating a job rarely
has visibility into every downstream consumer without deliberately looking.
**Owner:** Data Engineering, with mandatory input from the Data Consumers
interview.
**Inputs:** Outputs of every other methodology document in this folder
(each identifies *some* downstream consumers as a side effect), Hive query
logs, [`01-discovery/questions/08-data-consumers.md`](../../01-discovery/questions/08-data-consumers.md)
findings.

---

## What to look for

1. **Direct job-to-job consumers** — job B reads a table/path that job A
   writes. Already partially captured by
   [`01-spark-job-dependencies.md`](01-spark-job-dependencies.md) and
   [`02-hive-dependencies.md`](02-hive-dependencies.md) — this document
   consolidates that data specifically into a *reverse* index (per output,
   who consumes it), not just a forward index (per job, what it reads).
2. **BI tool / dashboard consumers** — every Tableau/Looker/Power BI
   dashboard or extract built directly on a Hive table, discovered via the
   Data Consumers interview and, where possible, BI-tool-side connection
   metadata (e.g., Tableau workbook data source inspection).
3. **Ad-hoc analyst query consumers** — surfaced via Hive/Spark Thrift
   Server query log mining (same technique as in
   [`02-hive-dependencies.md`](02-hive-dependencies.md)), specifically
   filtered to non-scheduled (interactive) query sessions.
4. **External/partner consumers** — any table or feed whose output is
   exported (via SFTP, REST API, or direct extract) to an external party,
   discovered via
   [`07-database-and-rest-api-dependencies.md`](07-database-and-rest-api-dependencies.md)
   and [`08-file-and-filesystem-dependencies.md`](08-file-and-filesystem-dependencies.md)
   findings.
5. **Shadow/undocumented automation** — scripts or notebooks built by
   individual analysts or engineers that read platform output on a
   schedule (personal cron jobs, scheduled notebook exports) but were never
   registered with the platform team. These are the hardest to find and
   the most likely to be missed.

## Technique

1. **Build the reverse index mechanically.** From the forward dependency
   data already gathered (job X reads path/table Y), invert it
   programmatically: for every path/table Y, list every job X that reads
   it. This is a data transformation, not new discovery work, and should
   be done first before manual investigation, since it's the cheapest and
   most complete source of downstream consumer data.
2. **Overlay query-log-derived consumers.** Add every table access found in
   Hive/Spark Thrift Server query logs (from
   [`02-hive-dependencies.md`](02-hive-dependencies.md) technique #3) that
   isn't already captured by the mechanical reverse index — these are the
   ad-hoc, non-job-based consumers.
3. **Confirm via the Data Consumers interview.** Cross-check the resulting
   list against
   [`01-discovery/questions/08-data-consumers.md`](../../01-discovery/questions/08-data-consumers.md)
   answers — self-reported usage often reveals consumers invisible to both
   code analysis and query logs (e.g., a manually downloaded CSV extract
   used to feed an external tool with no logged connection).
4. **Rank by consumer count and consumer criticality.** A table with many
   downstream consumers, or with even one Tier 1 downstream consumer, is a
   high-priority migration target for careful sequencing — it cannot move
   until its own dependencies are ready, but everything depending on it is
   blocked until it does move.

## Output format

Produce a **reverse dependency matrix**: rows are outputs (tables/paths),
columns list every known consumer (job ID, BI tool/dashboard name, external
partner, or "ad-hoc analyst — unregistered"), using the
[dependency matrix inventory template](../templates/03-dependency-matrix-inventory-template.md).

## Common Mistakes

- Stopping at the first hop — job A's output feeds job B, but job B's
  output might feed job C, D, and E. A change to job A can ripple three
  layers deep; only a full transitive closure of the reverse index reveals
  the true blast radius.
- Treating "no known consumers found" as proof a table is safe to
  deprioritize or drop, rather than as "no consumers found *yet*" —
  absence of evidence in logs/code is not the same as absence of a real
  consumer, especially for low-frequency (e.g., quarterly) usage.

## Production Notes

For every table feeding a Tier 1 job or a Tier 1 business function
(pricing, fraud, finance) anywhere in its consumer chain — even indirectly,
several hops downstream — that table itself should be treated with Tier 1
migration rigor (parallel-run, extended validation), regardless of how the
table's *producing* job was originally tiered.
