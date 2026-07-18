# Kafka Best Practices

## Consumer Group Management

### Fundamentals
- Each partition is consumed by exactly one consumer within a consumer group at any time.
- Number of consumers in a group should not exceed the number of partitions (excess consumers sit idle).
- Consumer assignment is managed by the group coordinator via rebalance protocol.

### Rebalance Optimization
- **Use `group.instance.id` (static membership):** Assigns a stable identity to each consumer. Brief restarts (within `session.timeout.ms`) skip rebalance entirely, preventing partition reassignment churn.
- **Use cooperative sticky assignor:** `partition.assignment.strategy=cooperative-sticky` minimizes partition movement during rebalance. Only revoked partitions are reassigned, not all.
- **Tune timeouts to match workload:**
  - `session.timeout.ms`: How long before coordinator considers consumer dead (default: 45s). Set higher for slow-processing consumers.
  - `heartbeat.interval.ms`: Frequency of heartbeats (default: 3s). Keep at 1/3 of session timeout.
  - `max.poll.interval.ms`: Max time between `poll()` calls (default: 5 min). Increase for batch processing with large batches.

### Consumer Configuration Checklist
```properties
# Reliability
enable.auto.commit=false           # Manual commit for at-least-once
auto.offset.reset=earliest         # Don't skip messages on new consumer
max.poll.records=500               # Control batch size per poll

# Performance
fetch.min.bytes=1048576            # 1 MB minimum fetch (reduce request frequency)
fetch.max.wait.ms=500              # Wait up to 500ms for min bytes
max.partition.fetch.bytes=1048576  # 1 MB per partition per fetch

# Stability
session.timeout.ms=45000
heartbeat.interval.ms=15000
max.poll.interval.ms=300000
```

## Exactly-Once Semantics

### Three Delivery Guarantees

| Guarantee | Producer Config | Consumer Config | Trade-off |
|-----------|----------------|-----------------|-----------|
| At-most-once | `acks=0` or `acks=1` | Auto-commit before process | Fastest, may lose messages |
| At-least-once | `acks=all`, `retries>0` | Commit after successful process | Safe, may duplicate |
| Exactly-once | `enable.idempotence=true` + transactional | Read-committed isolation | Slowest, no loss or duplication |

### Idempotent Producer
```properties
enable.idempotence=true    # Automatic with Kafka 3.0+
acks=all                   # Required for idempotence
retries=2147483647         # Max retries (default with idempotence)
max.in.flight.requests.per.connection=5  # Safe with idempotence
```
Idempotent producers assign sequence numbers to each message. Broker deduplicates retries within a producer session.

### Transactional Producer (Exactly-Once)
```properties
transactional.id=my-app-instance-1  # Unique per producer instance
enable.idempotence=true
```
Transactions span multiple topics/partitions atomically. Use for consume-transform-produce patterns.

### Consumer Side: Read Committed
```properties
isolation.level=read_committed  # Only see committed transactional messages
```

### Practical Exactly-Once with Beam
In Apache Beam on Dataflow, exactly-once is handled at the runner level:
- Beam's KafkaIO source commits offsets after successful processing.
- Dataflow's exactly-once mode deduplicates via checkpointing.
- For at-least-once mode, ensure downstream sinks are idempotent (e.g., BigQuery CDC with primary keys, Iceberg upsert).

## Schema Registry

### Avro vs JSON Schema vs Protobuf

| Feature | Avro | JSON Schema | Protobuf |
|---------|------|-------------|----------|
| Encoding | Binary (compact) | Text (verbose) | Binary (compact) |
| Schema evolution | Excellent | Limited | Good |
| Beam support | Native AvroIO | Manual parsing | GenericRecord |
| BQ Write API | Via conversion | Via conversion | Native support |
| Recommended for | High-throughput, evolving schemas | Human-readable, debugging | gRPC integration, BQ CDC |

### Schema Evolution Best Practices
1. **Use backward compatibility** (default in Confluent SR). New consumers can read old messages.
2. **Add fields with defaults.** Never add required fields without defaults.
3. **Mark fields deprecated** before removal. Remove only under full compatibility mode.
4. **Never rename fields** -- add new field, deprecate old one.
5. **Never change field types** -- add new field with new type.
6. **Register schemas in CI/CD** before deploying producers. Fail fast if incompatible.

### Compatibility Modes
- **BACKWARD (recommended default):** New schema can read data written with last schema.
- **FORWARD:** Old schema can read data written with new schema.
- **FULL:** Both backward and forward compatible.
- **NONE:** No compatibility checking (dangerous for production).

## Partition Strategy

### Choosing Partition Count
- **Rule of thumb:** Start with `max(num_consumers, expected_throughput_MB/s * 2)`.
- More partitions = more parallelism but more overhead (memory, file handles, rebalance time).
- Partitions can only be increased, never decreased. Start conservative.
- Target: 1-10 MB/s per partition for balanced throughput.

### Partition Key Selection
- **By entity ID** (e.g., member_id): Guarantees ordering per entity. Best for CDC and event sourcing.
- **By tenant/region:** Ensures data locality. Good for multi-tenant systems.
- **Round-robin (null key):** Maximum parallelism, no ordering. Good for stateless processing.
- **Custom partitioner:** Use when default hash distribution causes hot partitions.

### Hot Partition Prevention
- Monitor partition-level metrics. If one partition has 10x the throughput of others, the key distribution is skewed.
- Add salt to keys for high-cardinality hot keys: `key = f"{entity_id}_{hash(entity_id) % 4}"` (then aggregate downstream).
- Use compound keys to distribute: `region + entity_id` instead of just `entity_id`.

## Consumer Lag Monitoring

### Key Metrics
- **Consumer lag (offset):** Difference between log-end-offset and committed-offset per partition. This is the primary health indicator.
- **Consumer lag (time):** Estimated time to process backlog. More meaningful for SLAs.
- **Rebalance frequency:** Frequent rebalances indicate instability.
- **Commit rate:** Low commit rate with high lag indicates stuck consumers.

### Monitoring Setup
```
# Key JMX MBeans to export
kafka.consumer:type=consumer-fetch-manager-metrics,client-id=*
  - records-lag-max          # Maximum lag across all partitions
  - records-consumed-rate    # Throughput
  - fetch-latency-avg       # Fetch round-trip time

kafka.consumer:type=consumer-coordinator-metrics,client-id=*
  - rebalance-total          # Total rebalances
  - last-rebalance-seconds-ago
```

### Alert Thresholds (Starting Points)
- **Consumer lag > 10,000 offsets** for > 5 minutes: Warning.
- **Consumer lag > 100,000 offsets** for > 5 minutes: Critical.
- **Rebalance frequency > 3 per hour:** Investigate timeout/configuration.
- **No commits for > 2x max.poll.interval.ms:** Consumer likely stuck.

### Lag Recovery Strategies
1. **Scale consumers** up to partition count.
2. **Increase `max.poll.records`** if processing is fast but poll overhead is high.
3. **Increase `fetch.min.bytes`** to batch more data per request.
4. **Check for slow processing** in individual DoFns (profiling, external API latency).
5. **Temporary: skip** to latest offset (data loss) only for non-critical streams.

## Kafka + Beam Integration Patterns

### KafkaIO Read Configuration
```python
from apache_beam.io.kafka import ReadFromKafka

kafka_records = pipeline | ReadFromKafka(
    consumer_config={
        'bootstrap.servers': 'broker:9092',
        'group.id': 'my-beam-consumer',
        'auto.offset.reset': 'earliest',
        'security.protocol': 'SASL_SSL',
        'sasl.mechanism': 'PLAIN',
    },
    topics=['my-topic'],
    with_metadata=False,
    commit_offset_in_finalize=True,  # Commit after successful processing
    expansion_service=None,  # Auto-start Java expansion service
)
```

### Pattern: Kafka to Iceberg via Beam
```
Kafka Topic
    |
    v
KafkaIO.Read (Java cross-language)
    |
    v
beam.Map(parse_message)     # Deserialize JSON/Avro
    |
    v
beam.ParDo(TransformDoFn)   # Business logic + DLQ
    |
    +---> good --> managed.Write (Iceberg)
    |
    +---> bad  --> WriteToGCS (DLQ)
```

### Key Integration Considerations
- KafkaIO is a Java transform accessed via cross-language from Python.
- **Watermark:** Driven by Kafka consumer offset timestamp. Ensure producer sets event timestamps.
- **Checkpointing:** Dataflow checkpoints Kafka offsets. On restart, processing resumes from last checkpoint.
- **Scaling:** Number of Dataflow workers should be <= number of Kafka partitions for optimal parallelism.

## Error Handling

### Deserialization Failures
```python
class SafeDeserialize(beam.DoFn):
    def process(self, kafka_record):
        try:
            message = json.loads(kafka_record.value.decode('utf-8'))
            yield beam.pvalue.TaggedOutput('good', message)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            yield beam.pvalue.TaggedOutput('bad', {
                'raw_value': kafka_record.value.hex(),
                'topic': kafka_record.topic,
                'partition': kafka_record.partition,
                'offset': kafka_record.offset,
                'error': str(e),
            })
```

### Poison Pill Handling
A poison pill is a message that consistently fails processing, blocking consumer progress.

**Prevention:**
1. Always wrap deserialization in try/except with DLQ routing.
2. Set `max.poll.records` to limit blast radius.
3. Use schema validation at producer side (Schema Registry).

**Recovery:**
1. Route to DLQ and continue.
2. If DLQ not in place: manually advance consumer offset past the poison pill using `kafka-consumer-groups.sh --reset-offsets`.
3. Investigate root cause from DLQ records.

### Schema Mismatch Handling
When producers update schema without coordinating with consumers:
1. **Schema C pattern:** Message wrapped as `{"message": "<stringified JSON>"}`. Detect string-valued `message` key, parse inner JSON.
2. **Schema B pattern:** Message has nested `payload` containing actual data. Detect dict-valued `payload`, unwrap.
3. **Schema A pattern:** Flat message is the data itself.

Handle all variants in order of specificity (C -> B -> A) for maximum resilience.

---

*Sources: [Kafka Consumer Design](https://docs.confluent.io/kafka/design/consumer-design.html), [Delivery Semantics](https://docs.confluent.io/kafka/design/delivery-semantics.html), [Schema Registry Best Practices](https://www.confluent.io/blog/best-practices-for-confluent-schema-registry/), [Consumer Lag Monitoring](https://docs.confluent.io/platform/current/monitor/monitor-consumer-lag.html), [Partition Strategy](https://www.confluent.io/learn/kafka-partition-strategy/), [Consumer Rebalance Protocol](https://kafka.apache.org/41/operations/consumer-rebalance-protocol/)*
