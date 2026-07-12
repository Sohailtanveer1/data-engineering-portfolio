# Identifying Database and REST API Dependencies

**Purpose:** Jobs frequently reach outside the Hadoop platform entirely —
querying an operational RDBMS via Sqoop/JDBC, or calling an internal or
third-party REST API. These dependencies are grouped together here because
they share a discovery technique (connection string / endpoint
enumeration) despite being architecturally different.
**Owner:** Platform Engineering and Data Engineering.
**Inputs:** Sqoop job definitions, JDBC connection configuration, REST
client code, API gateway logs if available.

---

## What to look for — Databases

1. **Every Sqoop import/export job** — source/target database, table or
   query used, split-by column, and incremental-import watermark
   configuration (last-modified column or primary key checkpoint) if used.
2. **Direct JDBC reads from Spark** (`spark.read.jdbc(...)`) — connection
   string, credentials source, and query/table referenced.
3. **Connection pooling / shared connection configuration** — a common
   properties file referenced by multiple jobs, which becomes a
   shared-dependency migration point similar to shared JARs.
4. **Database-side load impact** — whether the source database has any
   rate-limiting or maintenance-window constraints that current Sqoop/JDBC
   jobs are designed around (e.g., "only extract during off-peak hours to
   avoid impacting OMS performance") — this constraint must carry forward
   to the GCP-side extraction design in
   [`06-data-migration/`](../../06-data-migration/README.md).

## What to look for — REST APIs

1. **Outbound calls** — every `curl`/`wget`/HTTP client library call in
   job code or shell scripts, extracting the target endpoint, HTTP method,
   authentication mechanism, and payload shape.
2. **Inbound calls** — any REST API this platform *exposes* to other
   systems (e.g., a fraud-scoring endpoint), which needs its own migration/
   redesign plan and cannot simply be "moved" the way a batch job can.
3. **Rate limits and SLAs** — documented or observed rate limits on
   third-party APIs, which constrain how migration-related backfill or
   parallel-run activity can safely call them without breaching quota.
4. **Authentication mechanism** — API key, OAuth token, mTLS certificate —
   and where the credential is currently stored (flag any plaintext
   storage per
   [`01-discovery/inventories/12-external-dependencies.md`](../../01-discovery/inventories/12-external-dependencies.md)).

## Technique

1. **Sqoop job definition enumeration.** List every Sqoop job definition
   (saved jobs via `sqoop job --list`, or script-embedded Sqoop commands)
   and extract connection strings, tables/queries, and incremental-import
   configuration.
2. **Connection string / endpoint grep.** Search all job code and shell
   scripts for JDBC URL patterns (`jdbc:...`), HTTP(S) URL patterns, and
   common HTTP client library imports/calls (`requests`, `HttpClient`,
   `curl`, `urllib`).
3. **API gateway / proxy log review (if available).** If outbound traffic
   passes through a proxy or API gateway, its logs are a strong independent
   cross-check against code-derived findings, surfacing calls made from
   configuration-driven or dynamically-constructed endpoints that static
   grep would miss.
4. **Source-system owner interview.** For every external database
   dependency, confirm with the owning team (per
   [`01-discovery/inventories/07-application-inventory.md`](../../01-discovery/inventories/07-application-inventory.md))
   what load/timing constraints apply — this cannot be discovered from code
   alone.

## Output format

Add findings to
[`01-discovery/inventories/12-external-dependencies.md`](../../01-discovery/inventories/12-external-dependencies.md),
explicitly noting authentication mechanism and any load/rate constraints.

## Common Mistakes

- Missing REST API calls made from within a library/utility function
  rather than directly in job code — grep the shared libraries identified
  in [`03-jar-library-shared-utility-dependencies.md`](03-jar-library-shared-utility-dependencies.md)
  too, not just top-level job code.
- Assuming a Sqoop incremental import's watermark logic will "just work"
  unchanged after migration — the watermark storage location and update
  mechanism must be explicitly redesigned for the GCP-native extraction
  pattern in [`06-data-migration/`](../../06-data-migration/README.md).

## Production Notes

For any dependency on the payment gateway or OMS database, coordinate
directly with the owning team before any migration-related testing that
would generate additional load — these are typically the most sensitive,
highest-governance systems in an ecommerce estate and unplanned load can
have direct customer impact.
