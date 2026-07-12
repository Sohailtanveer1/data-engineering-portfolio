# Identifying Shell Script and Cron Dependencies

**Purpose:** Shell scripts are the connective tissue of most on-prem Hadoop
estates — they wrap `spark-submit` calls, move files, check for markers,
and encode retry/error-handling logic that often isn't visible anywhere
else. Cron is frequently how these scripts get triggered, outside of any
central scheduler's visibility. Both must be inventoried explicitly, not
assumed to be simple wrappers.
**Owner:** Platform Engineering.
**Inputs:** All shell scripts referenced by scheduler definitions (Oozie
`shell` actions, Airflow `BashOperator` calls) and every crontab across
every edge/gateway node.

---

## What to look for

1. **Every crontab, on every node.** Not just the "primary" scheduler
   host — historically, individual data engineers or teams have added
   personal or team-specific cron entries directly on edge/gateway nodes
   outside central visibility. Check `/etc/cron.d/`, `/etc/crontab`, and
   `crontab -l` for every service account and every human user with shell
   access across every relevant node.
2. **What each script actually does**, not what its name suggests —
   `run_pricing_job.sh` might also silently clean up old files, check disk
   space, and send an email notification, none of which are obvious from
   the job name.
3. **Hardcoded paths, hostnames, and credentials** inside scripts — a very
   common pattern in shell wrappers, and every one found is a direct input
   to the "flagged findings" process in
   [`01-discovery/inventories/12-external-dependencies.md`](../../01-discovery/inventories/12-external-dependencies.md).
4. **Error handling and retry logic** — does the script check exit codes?
   Does it retry on failure, or does a silent failure in the middle of a
   pipeline just continue? This directly informs the idempotency and retry
   redesign required in
   [`07-spark-migration/`](../../07-spark-migration/README.md) and
   [`09-composer-migration/`](../../09-composer-migration/README.md).
5. **Marker file / success flag conventions** — scripts that check for or
   write `_SUCCESS`, `.done`, or similarly named marker files are encoding
   a data-availability dependency that needs to become an explicit
   Composer sensor/dependency, not a fragile file-existence check.
6. **Log rotation, cleanup, and "housekeeping" cron entries** — these are
   easy to overlook but their absence on the new platform can cause disk
   space or GCS lifecycle issues if not deliberately replaced (or
   confirmed unnecessary, since GCS lifecycle policies typically replace
   manual cleanup scripts entirely).

## Technique

1. **Full crontab sweep.** Script a sweep across every known edge/gateway
   node (from the inventory in
   [`03-current-environment/`](../../03-current-environment/README.md))
   that dumps every user's and every service account's crontab. Reconcile
   the resulting list against
   [`01-discovery/inventories/06-job-inventory.md`](../../01-discovery/inventories/06-job-inventory.md)
   — any cron entry with no matching Job ID is a discovery gap that must be
   resolved.
2. **Shell script static analysis.** Grep every referenced shell script for
   `spark-submit`, `hdfs dfs`, `hive -e`/`beeline`, `curl`/`wget` (REST/API
   calls), `sftp`/`scp`/`ftp` commands, and hardcoded credentials/paths.
3. **Call graph tracing.** Shell scripts frequently call other shell
   scripts (`source common_env.sh`, or direct invocation of a helper
   script). Trace the full call graph, not just the top-level script
   referenced by the scheduler, since shared wrapper scripts (like
   `common_env.sh`) are exactly the kind of shared dependency that needs
   careful handling similar to shared JARs.
4. **Ownership reconciliation.** For every cron entry, confirm an owning
   team/individual per
   [`01-discovery/questions/02-platform-team.md`](../../01-discovery/questions/02-platform-team.md)
   Q2 — orphaned cron entries with no known owner are common and must be
   individually investigated before being dropped.

## Output format

Add every discovered shell script and cron entry to
[`01-discovery/inventories/10-scheduler-inventory.md`](../../01-discovery/inventories/10-scheduler-inventory.md)
if not already present, and record hardcoded values found into
[`01-discovery/inventories/12-external-dependencies.md`](../../01-discovery/inventories/12-external-dependencies.md).

## Common Mistakes

- Treating a shell wrapper as "just calling Spark" and not reading it
  fully — the interesting dependencies (email notifications, marker files,
  secondary cleanup logic) are often in the parts of the script nobody
  looks at because they're not the "main" logic.
- Checking cron only on the officially designated scheduler host and
  missing entries on developer-accessible edge nodes.

## Production Notes

Shell scripts wrapping Tier 1 jobs should be fully rewritten (not
translated line-by-line) as part of
[`07-spark-migration/`](../../07-spark-migration/README.md) and
[`09-composer-migration/`](../../09-composer-migration/README.md) — shell
scripts accumulate undocumented complexity over years, and a business-
critical pipeline deserves a clean, reviewed reimplementation rather than a
faithful port of accumulated technical debt.
