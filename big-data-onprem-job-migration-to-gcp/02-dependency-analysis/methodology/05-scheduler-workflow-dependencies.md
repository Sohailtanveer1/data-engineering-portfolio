# Identifying Scheduler / Workflow Dependencies

**Purpose:** Beyond individual job dependencies, the *orchestration layer
itself* encodes dependencies — job A must finish before job B starts, job C
only runs if job A succeeded, job D waits for a data-availability signal.
This structural, inter-job dependency logic is what
[`09-composer-migration/`](../../09-composer-migration/README.md) must
translate faithfully — losing it produces jobs that individually "work" but
run in the wrong order or without their real preconditions met.
**Owner:** Platform Engineering, with Data Engineering review.
**Inputs:** Oozie coordinator and workflow XML, Airflow DAG source (if
partially adopted), cron-based dependency conventions (e.g., a script that
polls for another job's marker file).

---

## What to look for

1. **Explicit workflow ordering** — Oozie `<workflow-app>` action
   sequences, Airflow task dependencies (`>>`/`set_downstream`), or any
   documented "run B after A" convention.
2. **Conditional branching** — Oozie decision nodes, Airflow branch
   operators, or shell-script `if` logic that changes what runs next based
   on a prior step's outcome. This is the highest-risk category to lose in
   translation, since it often encodes real business logic (e.g., "if
   fraud score exceeds threshold, run additional review job").
3. **Data-availability triggers** — coordinators/DAGs that wait for a
   dataset to exist (a Hive partition, an HDFS marker file) rather than
   running on a pure time schedule. These require Composer sensor or
   deferrable-operator patterns, not a simple schedule translation — see
   [`09-composer-migration/`](../../09-composer-migration/README.md).
4. **Cross-coordinator/cross-DAG dependencies** — a job in one Oozie
   bundle waiting on output from a job defined in a completely separate
   bundle or system. These are the easiest inter-job dependencies to miss
   because they aren't visible within a single workflow definition.
5. **SLA and timeout configuration** — Oozie coordinator SLA tags or
   Airflow `sla`/`execution_timeout` settings, which encode the *current*
   operational expectation and should inform (though not blindly dictate)
   the SLA inventory in
   [`01-discovery/inventories/01-sla-inventory.md`](../../01-discovery/inventories/01-sla-inventory.md).

## Technique

1. **XML/DAG parsing.** Parse every Oozie coordinator and workflow XML file
   programmatically to extract the action graph — do not rely on manual
   reading alone for estates with more than a handful of workflows; use an
   XML parser to build a structured edge list (action → next action,
   including decision-node branches).
2. **Build the full DAG, not just the immediate neighbors.** For every job,
   trace both forward (what runs after it) and backward (what must run
   before it) through the entire workflow graph, not just one hop.
3. **Cross-reference against the job inventory.** Every node in an Oozie/
   Airflow graph should map to a Job ID in
   [`01-discovery/inventories/06-job-inventory.md`](../../01-discovery/inventories/06-job-inventory.md).
   Any workflow action with no corresponding inventory entry is a gap.
4. **Interview to confirm conditional logic intent.** For every decision
   node/branch found, confirm with the owning developer
   ([`01-discovery/questions/06-developers.md`](../../01-discovery/questions/06-developers.md))
   *why* the branch exists — static analysis shows *that* a branch exists,
   not necessarily the business reason, which matters for faithful
   Composer redesign.

## Output format

Produce a directed dependency graph per workflow/coordinator bundle using
the [dependency graph template](../templates/01-dependency-graph-template.md),
and feed the tabular edge list into
[`01-discovery/inventories/10-scheduler-inventory.md`](../../01-discovery/inventories/10-scheduler-inventory.md).

## Common Mistakes

- Translating Oozie coordinators to Composer DAGs one-to-one without first
  extracting the *complete* action graph including decision branches — this
  produces a DAG that runs the "normal path" correctly but silently drops
  the exception/branch handling.
- Missing cross-bundle dependencies because analysis was scoped to one
  Oozie bundle/Airflow DAG file at a time instead of the full orchestration
  estate.

## Production Notes

For every Tier 1 job's workflow graph, walk the full upstream chain back to
its ultimate data sources (not just its immediate predecessor task) and
confirm every node along that chain is itself scheduled for migration in a
wave that completes before or with the Tier 1 job — a Tier 1 job cannot be
migrated correctly if a Tier 3 job three steps upstream in its dependency
chain hasn't moved yet.
