#!/bin/bash
# run_pricing_nightly.sh — ON-PREM ORIGINAL shell wrapper.
#
# Invoked by the Oozie coordinator (pricing_nightly_coordinator.xml) via a
# <shell> action. This is the actual, real wrapper — captured as-is
# during 02-dependency-analysis/methodology/04-shell-script-and-cron-dependencies.md
# review. Do not fix warts here — see ../migration-record.md.
#
# Known issues:
#   - Hardcoded edge node path and spark-submit binary location
#   - client deploy-mode (driver runs on this edge node — a single
#     point of failure and the reason this script must run from
#     edge-node-03 specifically, undocumented anywhere except this file)
#   - No retry — a transient failure just fails, full stop
#   - Email alerting via local `mail`, easy to silently break if the
#     mail relay config on this specific node ever changes
#   - No structured exit-code-based alerting distinguishing a data
#     problem from an infra problem

set -e

RUN_DATE=$(date -d "yesterday" +%Y-%m-%d)
SPARK_SUBMIT=/opt/spark-2.4.8/bin/spark-submit
JOB_JAR_DIR=/home/svc_pricing_etl/jobs/pricing_nightly_batch
LOG_FILE=/var/log/pricing_jobs/pricing_nightly_${RUN_DATE}.log
ALERT_EMAIL="data-eng-pricing@acme.com"

echo "Starting pricing_nightly_batch for ${RUN_DATE}" >> "${LOG_FILE}"

${SPARK_SUBMIT} \
  --master yarn \
  --deploy-mode client \
  --queue pricing \
  --num-executors 40 \
  --executor-memory 8g \
  --executor-cores 4 \
  --driver-memory 4g \
  --conf spark.yarn.executor.memoryOverhead=1024 \
  "${JOB_JAR_DIR}/pricing_nightly_batch.py" "${RUN_DATE}" >> "${LOG_FILE}" 2>&1

EXIT_CODE=$?

if [ ${EXIT_CODE} -ne 0 ]; then
  echo "pricing_nightly_batch FAILED for ${RUN_DATE}, exit code ${EXIT_CODE}" >> "${LOG_FILE}"
  mail -s "[FAILED] pricing_nightly_batch ${RUN_DATE}" "${ALERT_EMAIL}" < "${LOG_FILE}"
  exit ${EXIT_CODE}
fi

echo "pricing_nightly_batch SUCCESS for ${RUN_DATE}" >> "${LOG_FILE}"

# Cleanup: remove log files older than 30 days. No GCS-lifecycle
# equivalent existed on-prem, so this was hand-rolled per job.
find /var/log/pricing_jobs/ -name "pricing_nightly_*.log" -mtime +30 -delete
