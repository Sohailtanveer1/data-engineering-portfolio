# Initialization Actions & Custom Images

**Purpose:** Define how cluster-level dependencies (beyond what's handled
by job-level `python_file_uris`/`jar_file_uris`) are installed —
consistently, version-controlled, and without manual, imperative
configuration of running clusters.
**Owner:** Platform Engineering.

---

## When to use an initialization action vs. a custom image

| Situation | Approach |
|---|---|
| A lightweight, fast-installing dependency (a small OS package, a monitoring agent) | Initialization action script, run at cluster startup |
| A heavy dependency (a large ML library, many OS packages) that would meaningfully slow every ephemeral cluster's startup time if installed via init action on every run | Custom Dataproc image, pre-baked with the dependency, used as the cluster's base image |
| No special dependency beyond the shared Spark library and standard Dataproc image contents | Neither — use the standard Dataproc image directly |

For ephemeral, frequently-recreated clusters, minimizing startup time
matters — prefer custom images over init actions for anything with
non-trivial install time, since init actions run fresh on every single
cluster creation.

## Initialization action example

```bash
#!/bin/bash
# init-actions/install-monitoring-agent.sh
# Stored and versioned in scripts/, referenced from Terraform cluster config.
set -euo pipefail

# Install a lightweight custom monitoring agent not included in the
# standard Dataproc image, required for [specific platform-level
# monitoring need — document the actual reason here, not just "we need this"].
apt-get update && apt-get install -y custom-monitoring-agent
systemctl enable custom-monitoring-agent
systemctl start custom-monitoring-agent
```

Referenced in the Terraform cluster module:

```hcl
cluster_config {
  initialization_action {
    script      = "gs://${var.artifact_bucket}/init-actions/install-monitoring-agent.sh"
    timeout_sec = 300
  }
}
```

## Custom image build process

1. Define the custom image's additional requirements (OS packages, large
   libraries) in a version-controlled Dockerfile-equivalent build
   specification (Dataproc custom image tooling, per Google's
   `generate_custom_image.py` pattern or equivalent).
2. Build and publish the custom image via
   [`ci-cd/`](../ci-cd/README.md) on a defined schedule (e.g., monthly, or
   triggered by a base Dataproc image update) — not built ad-hoc or
   manually.
3. Version the custom image explicitly (e.g.,
   `dataproc-custom-<job-family>-<date>`), and reference a specific
   version from each job family's cluster configuration — never `latest`,
   consistent with the versioning discipline established in
   [`07-spark-migration/04-packaging-and-dependency-management.md`](../07-spark-migration/04-packaging-and-dependency-management.md).

## Keeping custom images current

Custom images must be rebuilt when the underlying Dataproc base image
receives security patches — establish a periodic rebuild cadence (not
"whenever someone remembers") and track it in
[`documentation/`](../documentation/README.md) as an operational
responsibility with a named owner.

## Common Mistakes

- Using initialization actions for a heavy dependency that materially
  slows every ephemeral cluster's startup, silently degrading job SLA
  through cumulative startup overhead across many runs.
- Building a custom image once and never rebuilding it, causing the
  platform to run on an increasingly outdated (and eventually
  unpatched/insecure) base image.

## Production Notes

Measure the actual startup time impact of any initialization action used
by a Tier 1 job family — if it materially affects that job's SLA margin
(per
[`01-discovery/inventories/01-sla-inventory.md`](../01-discovery/inventories/01-sla-inventory.md)),
migrate it to a custom image instead, even if the individual install seems
fast in isolation.
