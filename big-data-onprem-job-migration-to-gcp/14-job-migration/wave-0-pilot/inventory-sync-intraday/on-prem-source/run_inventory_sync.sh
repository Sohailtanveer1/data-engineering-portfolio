#!/bin/bash
# run_inventory_sync.sh — ON-PREM ORIGINAL shell wrapper.
#
# Invoked directly by cron every 15 minutes (see crontab-entry.txt) — no
# Oozie involved for this job, unlike pricing_nightly_batch. Captured
# during 02-dependency-analysis/methodology/04-shell-script-and-cron-dependencies.md
# review.
#
# Known issues: no retry, no alerting on failure at all (confirmed during
# 01-discovery/questions/07-operations.md — this job's silent-failure gap
# is a real, named finding, not hypothetical).

set -e

WINDOW_ID=$(date +%Y-%m-%dT%H%M)
SPARK_SUBMIT=/opt/spark-2.4.8/bin/spark-submit
JOB_DIR=/home/svc_inventory_etl/jobs/inventory_sync_intraday
LOG_FILE=/var/log/inventory_jobs/inventory_sync_$(date +%Y%m%d).log

echo "Starting inventory_sync_intraday for window ${WINDOW_ID}" >> "${LOG_FILE}"

${SPARK_SUBMIT} \
  --master yarn \
  --deploy-mode client \
  --queue inventory \
  --num-executors 15 \
  --executor-memory 4g \
  --executor-cores 4 \
  --driver-memory 2g \
  "${JOB_DIR}/inventory_sync_intraday.py" "${WINDOW_ID}" >> "${LOG_FILE}" 2>&1

# No failure branch here — if spark-submit fails, `set -e` kills the
# script, cron logs a non-zero exit to its own mail spool (rarely
# checked), and no one is proactively notified. This is exactly the gap
# closed in the migrated version's alerting.
echo "inventory_sync_intraday finished for window ${WINDOW_ID}" >> "${LOG_FILE}"
