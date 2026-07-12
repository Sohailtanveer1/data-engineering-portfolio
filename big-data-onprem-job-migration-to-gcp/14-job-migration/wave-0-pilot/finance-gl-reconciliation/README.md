# Wave 0 Pilot — `finance_gl_reconciliation`

Third real job migration in the Wave 0 pilot — see
[`migration-record.md`](migration-record.md). The only one of the three
pilot jobs with **no Spark/Dataproc at all** (Hive → BigQuery directly),
and the only one whose tests were **actually executed and passing**
(16/16) in this authoring environment, since its validation logic is
pure Python with no JVM dependency.

## Contents

| Folder/File | What It Is |
|---|---|
| [`on-prem-source/`](on-prem-source/) | The real job: Hive `.hql`, shell wrapper (with a confirmed, real year-boundary bug), Oozie coordinator |
| [`dependency-analysis.md`](dependency-analysis.md) | Filled-in dependency card |
| [`migrated-gcp/`](migrated-gcp/) | Complete migration: BigQuery `MERGE` SQL, the balance-check gate that never existed on-prem, the fiscal-period bug fix, Composer DAG (no Dataproc) |
| [`migration-record.md`](migration-record.md) | What changed, why, and **actually-verified** test results |

## Run the tests yourself

No JVM needed for this one:

```bash
cd migrated-gcp
pip install -e ".[dev]"
pytest tests/ -v
# 16 passed
```
