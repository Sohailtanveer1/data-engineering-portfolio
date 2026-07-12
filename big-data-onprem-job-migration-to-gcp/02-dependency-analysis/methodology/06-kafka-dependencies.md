# Identifying Kafka Dependencies

**Purpose:** Where Kafka is present (confirmed per
[`01-discovery/`](../../01-discovery/README.md) — this platform description
lists it as conditional), streaming dependencies carry different risks than
batch dependencies: topic schema evolution, consumer group offset
management, and at-least-once/exactly-once delivery semantics all need to
be understood before deciding whether to migrate to Pub/Sub, self-managed
Kafka on GCE, or a managed Kafka offering.
**Owner:** Platform Engineering, with the streaming job owners identified
in [`01-discovery/inventories/08-spark-inventory.md`](../../01-discovery/inventories/08-spark-inventory.md).
**Inputs:** Kafka broker configuration, topic list, consumer group
registrations, Spark Structured Streaming job source code.

---

## What to look for

1. **Topic inventory** — every topic, its partition count, replication
   factor, retention policy, and message format (Avro/JSON/Protobuf, and
   whether a Schema Registry is in use).
2. **Producers** — every job/system writing to each topic, and whether
   writes are idempotent (Kafka producer idempotence config) or
   at-least-once with downstream deduplication expected.
3. **Consumers and consumer groups** — every job reading from each topic,
   its consumer group ID, and current offset management strategy
   (auto-commit vs. manual commit, and where offsets are checkpointed for
   Spark Structured Streaming jobs — critical for a lossless migration
   cutover).
4. **Schema evolution history** — has the topic's schema changed over
   time, and are consumers tolerant of older message versions still
   possibly in the topic (relevant for backlog/replay scenarios during
   migration)?
5. **Delivery semantics requirements** — does the business requirement for
   this topic tolerate at-least-once (possible duplicates, handled
   downstream) or does it require exactly-once? This is a hard input to
   the target architecture decision in
   [`04-target-architecture/`](../../04-target-architecture/README.md).

## Technique

1. **Broker-side topic enumeration.** Use `kafka-topics.sh --list` and
   `--describe` (or the equivalent admin API) to get the authoritative
   topic list, partition counts, and configuration — do not rely on a
   wiki-documented topic list, which drifts.
2. **Consumer group inspection.** Use `kafka-consumer-groups.sh --describe`
   to enumerate active consumer groups and their current lag — this also
   surfaces "zombie" consumer groups from retired jobs still technically
   registered.
3. **Producer/consumer code cross-reference.** Grep Spark Structured
   Streaming and any other Kafka client code for topic names and consumer
   group IDs, cross-referencing against the job inventory.
4. **Schema Registry audit (if present).** Pull the full schema history per
   topic/subject to understand compatibility mode (backward/forward/full)
   in use, since this determines whether historical topic data can be
   safely replayed against newer consumer code.

## Output format

Add a Kafka-specific section to
[`01-discovery/inventories/12-external-dependencies.md`](../../01-discovery/inventories/12-external-dependencies.md)
covering: topic name, producers, consumers, retention, delivery-semantics
requirement, and proposed GCP target (Pub/Sub vs. self-managed/managed
Kafka — decided formally in
[`04-target-architecture/`](../../04-target-architecture/README.md)).

## Common Mistakes

- Assuming all topics can migrate to Pub/Sub with equivalent semantics
  without checking exactly-once/ordering requirements — Pub/Sub's delivery
  and ordering guarantees differ from Kafka's and must be explicitly
  compared per topic, not assumed equivalent.
- Missing "zombie" consumer groups that no longer have an active job behind
  them but are still consuming/committing offsets, silently skewing lag
  metrics used for capacity planning.

## Production Notes

If any Kafka topic feeds a Tier 1 job (e.g., fraud scoring), the migration
approach must include a documented plan for **zero-message-loss cutover**
— likely a dual-write or dual-consume parallel-run period — designed
explicitly in [`06-data-migration/`](../../06-data-migration/README.md),
not left as an implementation detail.
