# Discovery Questions — Developers (Job Owners / Engineers)

**Purpose:** Developers know the implementation details, quirks, and
technical debt of the jobs they wrote or maintain — information that's
essential to [`02-dependency-analysis/`](../../02-dependency-analysis/README.md)
and [`07-spark-migration/`](../../07-spark-migration/README.md) and that
exists nowhere else if undocumented.
**Owner:** Migration Program Lead, conducted with Platform/Data Engineering
leads facilitating access to individual job owners.
**Audience:** Engineers who write, own, or maintain Spark jobs, Hive DDL,
shell scripts, and scheduler workflows.

---

## Questions

| # | Question | Why we ask it |
|---|---|---|
| 1 | For the jobs you own, what does each one actually do, in plain language (not just the job name)? | Job names ("job_47_final_v2") are frequently uninformative; this is often the only way to reconstruct true purpose before migration. |
| 2 | What upstream data does each job read, and from where (HDFS paths, Hive tables, Kafka topics, external systems)? | Core input to [`02-dependency-analysis/`](../../02-dependency-analysis/README.md) — must be captured per job, not assumed from job name. |
| 3 | What downstream systems or jobs consume this job's output? | Missing a downstream consumer is the most common cause of a "silent" post-migration break — feeds the dependency graph. |
| 4 | Are there hardcoded paths, hostnames, credentials, or configuration values in the code? | Every hardcoded value is a guaranteed migration blocker; this must be enumerated before packaging work in [`07-spark-migration/`](../../07-spark-migration/README.md) begins. |
| 5 | Does this job depend on any shared library, JAR, or utility script outside its own repo? | Shared dependencies must be migrated/rebuilt once, correctly, rather than discovered piecemeal per job — feeds [`02-dependency-analysis/`](../../02-dependency-analysis/README.md). |
| 6 | Is this job idempotent — can it be safely re-run against the same input without side effects or duplicate output? | Idempotency is a hard requirement for the new platform's retry model in [`07-spark-migration/`](../../07-spark-migration/README.md); non-idempotent jobs need explicit redesign, not just re-platforming. |
| 7 | Are there known bugs, workarounds, or "don't touch this" parts of the code? | Undocumented workarounds often encode real (if ugly) business logic that must be preserved, not "cleaned up" accidentally during migration. |
| 8 | What Spark/Scala/Python/Hive version-specific features or deprecated APIs does this code use? | Directly scopes the API-migration work in [`07-spark-migration/`](../../07-spark-migration/README.md). |
| 9 | How is this job currently tested (if at all) before deployment? | Determines whether existing tests can be reused/ported or whether test coverage must be built from scratch as part of migration — feeds [`15-testing/`](../../15-testing/README.md). |
| 10 | If you left the company tomorrow, what about this job would be lost that isn't written down anywhere? | The single most important question in this interview — it directly targets tribal knowledge (risk R8 in the program risk register) before it's lost. |
| 11 | Which of your jobs would you personally be most nervous about migrating, and why? | Developer intuition about fragility is a strong, fast signal for prioritizing which jobs need extra validation/parallel-run time. |
| 12 | Are there any jobs you maintain that you believe are no longer needed / could be retired instead of migrated? | Every job retired instead of migrated is scope removed cleanly — always worth asking explicitly rather than assuming everything must move. |

## Validation of answers

Cross-reference claimed dependencies against static code analysis (grep for
hardcoded paths/hosts, JAR manifest inspection) performed in
[`02-dependency-analysis/`](../../02-dependency-analysis/README.md) — developer
memory of "what this job touches" is a strong start but is regularly
incomplete for code the developer didn't originally write.
