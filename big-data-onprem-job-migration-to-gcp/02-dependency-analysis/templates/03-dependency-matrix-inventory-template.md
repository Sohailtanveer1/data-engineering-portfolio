# Template — Dependency Matrix Inventory (Master Roll-Up)

**Purpose:** A single spreadsheet-style master matrix rolling up every
per-job dependency card into one view, used to spot cross-cutting patterns
(widely-shared libraries, heavily-consumed tables, jobs with the most
unresolved dependency risk) that aren't visible from individual cards.
**Owner:** Migration Program Lead, populated from completed
[job dependency cards](02-job-dependency-card-template.md).
**When to use:** Once a meaningful batch of job dependency cards is
complete (recommended: complete this roll-up after every 20-30 cards, not
only at the very end, so patterns can inform wave planning early).

---

## Master dependency matrix

| Job ID | Tier | # Upstream Deps | # Downstream Consumers | Uses Shared Lib(s) | External System Deps | Unresolved Risk Flags | Validation Status | Ready for Wave Planning? |
|---|---|---|---|---|---|---|---|---|
| EX-001 | 1 | 4 | 3 | `internal-fraud-utils` | Kafka, SFTP | Deprecated APIs | 2-technique confirmed | Yes |
| EX-002 | 1 | 2 | 5 | none | Kafka | Not confirmed idempotent | 2-technique confirmed | Blocked — idempotency fix required first |
| EX-007 | 4 | 1 | 0 | none | Sqoop (unknown source DB) | Owner unconfirmed | 1-technique only | Blocked — owner investigation required |

_(Illustrative rows — populate by aggregating completed dependency cards.)_

## Cross-cutting analysis views

Build these summary views from the matrix once populated — each answers a
different planning question:

### 1. Shared library / JAR reuse ranking

| Shared Library | # Jobs Depending On It | Highest Tier Among Dependents | Migration Priority |
|---|---|---|---|
| `internal-fraud-utils` | 12 | Tier 1 | Highest — rebuild and validate first in `07-spark-migration/` |

### 2. Most-consumed tables/outputs (from downstream consumer analysis)

| Table/Output | # Downstream Consumers | Highest Tier Among Consumers | Migration Priority |
|---|---|---|---|
| `pricing.daily_price_snapshot` | 6 | Tier 1 | High — cannot move until every consumer is ready or in parallel-run |

### 3. Jobs blocked from wave planning

| Job ID | Blocking Issue | Owner of Resolution | Target Resolution Date |
|---|---|---|---|
| EX-002 | Not confirmed idempotent | Platform Engineering | _(date)_ |
| EX-007 | No confirmed owner | Migration Program Lead | _(date)_ |

### 4. Dependency risk heatmap (for wave sequencing input)

Rank every job by a simple composite score — e.g., (# unresolved risk
flags × 2) + (# downstream Tier-1 consumers) — to get an objective,
repeatable input into
[`14-job-migration/`](../../14-job-migration/README.md) wave prioritization,
rather than sequencing waves on intuition alone.

## How this feeds later phases

- Jobs with zero unresolved risk flags and full validation become
  candidates for **early, low-risk migration waves** — they prove the
  pattern with minimal exposure.
- Jobs feeding the "blocked" list must be resolved before entering any
  wave plan — see [`14-job-migration/`](../../14-job-migration/README.md).
- The shared-library reuse ranking directly sequences build order in
  [`07-spark-migration/`](../../07-spark-migration/README.md).
