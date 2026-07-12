#!/bin/bash
# init-actions/install-monitoring-agent.sh
#
# Dataproc initialization action — installs a lightweight monitoring
# agent not included in the standard Dataproc image.
# See 12-cluster-design/07-initialization-actions-and-custom-images.md.
#
# Referenced from the Terraform cluster module via:
#   initialization_action_scripts = ["gs://<artifact-bucket>/init-actions/install-monitoring-agent.sh"]

set -euo pipefail

readonly LOG_PREFIX="[init-action:monitoring-agent]"

echo "${LOG_PREFIX} Starting installation"

# Only run on worker nodes if this agent is worker-specific — the
# ROLE metadata attribute is set automatically by Dataproc.
ROLE=$(/usr/share/google/get_metadata_value attributes/dataproc-role || echo "unknown")
echo "${LOG_PREFIX} Node role: ${ROLE}"

apt-get update -qq
apt-get install -y -qq custom-monitoring-agent

systemctl enable custom-monitoring-agent
systemctl start custom-monitoring-agent

# Verify the agent actually started — an initialization action that
# exits 0 without confirming success can silently produce a cluster
# with a "configured" but non-functional monitoring agent.
if ! systemctl is-active --quiet custom-monitoring-agent; then
  echo "${LOG_PREFIX} ERROR: custom-monitoring-agent failed to start" >&2
  exit 1
fi

echo "${LOG_PREFIX} Installation complete, agent running"
