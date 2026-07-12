# Identifying Hive Dependencies

**Purpose:** Establish a repeatable method for discovering which jobs,
views, and external consumers depend on a given Hive table — and which
tables a given job's Hive queries depend on — since Hive dependencies are
often invisible in job source code (they live in SQL strings or separate
`.hql` files).
**Owner:** Data Engineering.
**Inputs:** `.hql` files, embedded `spark.sql(...)` string literals, Hive
Metastore catalog, Hive/Spark Thrift Server query logs.

---

## What to look for

1. **Table and view references inside SQL** — every `FROM`, `JOIN`,
   `INSERT INTO`/`INSERT OVERWRITE` target across all `.hql` scripts and
   embedded SQL strings in Spark jobs.
2. **View chains** — a view built on a view built on a table is a common
   pattern; the true base-table dependency is often several layers removed
   from what a query author sees. Resolve the full chain, not just the
   immediate reference.
3. **Metastore-level table properties** — storage location, SerDe,
   partitioning scheme, and any custom table properties (e.g.,
   TBLPROPERTIES referencing an external system) recorded in
   `DESCRIBE FORMATTED <table>`.
4. **Cross-database references** — queries that join across Hive
   databases owned by different teams; these are prime candidates for
   coordination gaps if the two databases end up migrated to GCP on
   different timelines.

## Technique

1. **Static SQL parsing.** Grep/parse every `.hql` file and every
   `spark.sql("...")` / `sqlContext.sql("...")` string literal in job code
   for table references. For accuracy at scale, use a SQL parser (e.g., a
   lightweight ANTLR-based Hive/Spark SQL grammar) rather than pure regex,
   since regex over-matches and under-matches on complex queries.
2. **Metastore catalog walk.** Programmatically query the Metastore
   backing database (or use `SHOW TABLES`/`DESCRIBE FORMATTED` via Hive
   CLI/Beeline scripted across every database) to build the authoritative
   table/view/column list — this is the source of truth the SQL parsing
   step above is checked against.
3. **Query log mining.** If Hive/Spark Thrift Server or HiveServer2 query
   logs are retained, mine them for actual table access over a
   representative window (ideally including a peak period and a
   month-end/quarter-end period) — this surfaces tables accessed by
   ad-hoc/analyst queries that never appear in any scheduled job's source
   code.
4. **View dependency resolution.** For every view, recursively resolve its
   `SHOW CREATE VIEW` definition until reaching base tables, building the
   full lineage chain, not just the first hop.

## Output format

Feed findings into the Hive inventory
([`01-discovery/inventories/09-hive-inventory.md`](../../01-discovery/inventories/09-hive-inventory.md))
"Consumers" column, and into per-job dependency cards for any job whose SQL
was parsed.

## Common Mistakes

- Parsing only `.hql` files and missing SQL embedded as string literals
  inside Spark job source code — in mixed estates, a significant fraction
  of Hive access happens through `spark.sql()` calls, not standalone HQL
  scripts.
- Treating a view's dependencies as fully captured by its immediate
  `SHOW CREATE VIEW` output without recursing through nested views.
- Ignoring query logs entirely and relying only on scheduled job source —
  this misses every ad-hoc analyst query, which is exactly the category
  most likely to break silently and surface during
  [`20-uat/`](../../20-uat/README.md) instead of before.

## Production Notes

For any table found in the `pricing`, `fraud`, or `finance` Hive databases
(per [`01-discovery/inventories/09-hive-inventory.md`](../../01-discovery/inventories/09-hive-inventory.md)),
run the query-log-mining technique over a full fiscal quarter, not just a
30-day window — some finance-adjacent queries only run at quarter-end and
will be invisible in a shorter sampling window.
