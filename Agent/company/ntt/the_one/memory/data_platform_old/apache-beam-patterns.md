# Apache Beam Design Patterns

## Pipeline Design Patterns

### Fan-Out (One-to-Many)
Apply multiple transforms to the same PCollection independently. Each branch processes independently and can run in parallel.

```python
input_pcoll = pipeline | 'Read' >> ReadFromSource()

# Fan-out: same input, different processing paths
enriched = input_pcoll | 'Enrich' >> beam.ParDo(EnrichDoFn())
filtered = input_pcoll | 'Filter' >> beam.Filter(is_valid)
metrics  = input_pcoll | 'Metrics' >> beam.CombineGlobally(CountCombineFn())
```

### Fan-In (Many-to-One)
Merge multiple PCollections using `Flatten` (union) or `CoGroupByKey` (join by key).

```python
# Union: combine same-schema PCollections
merged = (branch_a, branch_b) | 'Merge' >> beam.Flatten()

# Join: combine by shared key
joined = {'left': left_pcoll, 'right': right_pcoll} | beam.CoGroupByKey()
```

### Side Inputs
Pass additional data to a DoFn as read-only context. Useful for lookup tables, configuration, or small reference datasets.

```python
# Side input as dict (must fit in memory per worker)
lookup = pipeline | 'LoadLookup' >> beam.Create(lookup_data)

results = main_pcoll | beam.ParDo(
    LookupDoFn(),
    lookup_dict=beam.pvalue.AsDict(lookup)
)
```

**Caution:** Side inputs are materialized in memory on every worker. For large datasets (> 100 MB), consider using a keyed join or external lookup (API call with caching) instead.

### Shared State Pattern (setup/teardown)
Use `DoFn.setup()` to initialize expensive resources (HTTP clients, DB connections) once per worker, shared across all bundles.

```python
class ApiCallDoFn(beam.DoFn):
    def setup(self):
        self.client = httpx.Client(timeout=30)
    
    def process(self, element):
        response = self.client.get(f"/api/{element['id']}")
        yield response.json()
    
    def teardown(self):
        self.client.close()
```

## DoFn Lifecycle

```
                        +-----------+
                        |  setup()  |  -- Once per DoFn instance (worker initialization)
                        +-----+-----+
                              |
                   +----------+-----------+
                   |                      |
            +------v-------+     +-------v------+
            | start_bundle |     | start_bundle |  -- Once per bundle
            +------+-------+     +-------+------+
                   |                      |
            +------v-------+     +-------v------+
            |  process()   |     |  process()   |  -- Once per element
            |  process()   |     |  process()   |
            |  process()   |     |  process()   |
            +------+-------+     +-------+------+
                   |                      |
            +------v--------+    +-------v-------+
            | finish_bundle |    | finish_bundle |  -- Once per bundle
            +------+--------+    +-------+-------+
                   |                      |
                   +----------+-----------+
                              |
                        +-----v------+
                        | teardown() |  -- Best effort, NOT guaranteed
                        +------------+
```

### Lifecycle Method Guidelines

| Method | When | Use For | Guarantees |
|--------|------|---------|------------|
| `setup()` | Once per instance | Init clients, load models, open connections | Called before any processing |
| `start_bundle()` | Once per bundle | Reset batch buffers, start transactions | Called before process() |
| `process()` | Once per element | Core transformation logic | Elements in a bundle are sequential |
| `finish_bundle()` | Once per bundle | Flush batch buffers, commit transactions | Called after all process() in bundle |
| `teardown()` | Once per instance | Close connections, release resources | **Best effort only** -- may not be called |

### Key Rules
- DoFn instances are **serialized and deserialized** across workers. All instance state set before `setup()` must be serializable.
- `teardown()` is not guaranteed. Do not rely on it for critical cleanup (e.g., flushing writes). Use `finish_bundle()` for that.
- Bundle size is runner-determined. Streaming bundles are typically smaller (1-1000 elements). Batch bundles can be much larger.
- DoFn instances may be reused across bundles. Do not assume a fresh instance per bundle.

## Windowing

### Fixed Windows
Uniform, non-overlapping time intervals.
```python
pcoll | beam.WindowInto(beam.window.FixedWindows(60))  # 60-second windows
```
**Use for:** Regular aggregation intervals (per-minute counts, hourly summaries).

### Sliding Windows
Overlapping windows. Each element can belong to multiple windows.
```python
pcoll | beam.WindowInto(beam.window.SlidingWindows(300, 60))  # 5-min window, 1-min slide
```
**Use for:** Moving averages, rolling statistics. Note: elements are duplicated across overlapping windows, increasing processing cost.

### Session Windows
Dynamic windows based on activity gaps. Elements within the gap duration are grouped.
```python
pcoll | beam.WindowInto(beam.window.Sessions(600))  # 10-min gap
```
**Use for:** User activity sessions, transaction groups.

### Global Window
Single window for all elements (default for bounded PCollections).
```python
pcoll | beam.WindowInto(beam.window.GlobalWindows())
```
**Use for:** Batch processing, or streaming per-element transforms with triggers.

### Triggers
Control when window results are emitted:
```python
pcoll | beam.WindowInto(
    beam.window.FixedWindows(60),
    trigger=AfterWatermark(
        early=AfterProcessingTime(30),   # Emit partial results every 30s
        late=AfterCount(1)               # Emit on each late element
    ),
    accumulation_mode=AccumulationMode.ACCUMULATING,
    allowed_lateness=Duration(seconds=3600)  # Accept late data for 1 hour
)
```

## State and Timers

### State API
Per-key, per-window mutable state. Requires keyed PCollection.

```python
class StatefulCounter(beam.DoFn):
    COUNT_STATE = BagStateSpec('count', VarIntCoder())
    
    def process(self, element, count=beam.DoFn.StateParam(COUNT_STATE)):
        current = sum(count.read()) or 0
        count.clear()
        count.add(current + 1)
        yield element[0], current + 1
```

### State Types
- **ValueState:** Single value per key.
- **BagState:** Append-only collection.
- **SetState:** Deduplicated collection.
- **CombiningState:** Incrementally combined value (like CombineFn).

### Timer API
Deferred callbacks for delayed processing.

```python
class BufferedWriter(beam.DoFn):
    BUFFER = BagStateSpec('buffer', PickleCoder())
    FLUSH_TIMER = TimerSpec('flush', TimeDomain.PROCESSING_TIME)
    
    def process(self, element, 
                buffer=beam.DoFn.StateParam(BUFFER),
                flush=beam.DoFn.TimerParam(FLUSH_TIMER)):
        buffer.add(element)
        flush.set(Timestamp.now() + Duration(seconds=30))
    
    @on_timer(FLUSH_TIMER)
    def on_flush(self, buffer=beam.DoFn.StateParam(BUFFER)):
        batch = list(buffer.read())
        buffer.clear()
        yield batch  # Flush accumulated elements
```

**Important:** Garbage collect state explicitly. State persists per key/window and can cause memory leaks if not cleared when no longer needed.

## Cross-Language Transforms (Java IcebergIO from Python)

Beam's multi-language pipeline framework allows Python pipelines to use Java transforms via an expansion service.

### How It Works
1. Python SDK sends transform specification to a Java expansion service.
2. Java expansion service returns the expanded pipeline graph.
3. Runner executes both Python and Java portions, with data serialized via Beam Row schema.

### IcebergIO from Python (via managed.Write)
```python
from apache_beam.transforms.managed import Write

pcoll | Write(
    config={
        "table": "catalog.namespace.table_name",
        "catalog_name": "my_catalog",
        "catalog_properties": {
            "type": "rest",
            "uri": "https://biglake.googleapis.com/iceberg/v1/restcatalog",
            "warehouse": "gs://my-bucket",
        }
    }
)
```

### Key Considerations
- Java expansion service starts automatically on Dataflow (no manual setup).
- Schema mapping between Python and Java uses Beam Row (named fields with types).
- Performance: Cross-language serialization adds overhead. Batch large elements before cross-language boundary.
- Version alignment: Python SDK and Java IcebergIO versions must be compatible.

## Error Handling

### Dead Letter Queue (DLQ) with Tagged Outputs
```python
class ProcessWithDLQ(beam.DoFn):
    def process(self, element):
        try:
            result = transform(element)
            yield beam.pvalue.TaggedOutput('good', result)
        except Exception as e:
            yield beam.pvalue.TaggedOutput('bad', {
                'element': element,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })

results = input_pcoll | beam.ParDo(ProcessWithDLQ()).with_outputs('good', 'bad')

# Write good results to primary sink
results.good | 'WriteGood' >> WriteToSink()

# Write failed elements to DLQ
results.bad | 'WriteDLQ' >> WriteToGCS('gs://bucket/dlq/')
```

### Automatic Exception Handling (Beam 2.50+)
```python
results = input_pcoll | beam.ParDo(MyDoFn()).with_exception_handling(
    main_tag='good',
    dead_letter_tag='bad',
    exc_class=Exception
)
```

### BigQuery Failed Rows
```python
result = pcoll | beam.io.WriteToBigQuery(
    table='project:dataset.table',
    method='STREAMING_INSERTS',
    insert_retry_strategy='RETRY_ON_TRANSIENT_ERROR'
)
# Access failed rows
result['FailedRows'] | 'HandleFailures' >> beam.Map(log_failure)
```

## Testing

### Unit Test DoFns with DirectRunner
```python
def test_my_dofn():
    with TestPipeline() as p:
        input_pcoll = p | beam.Create([{'id': 1}, {'id': 2}])
        output = input_pcoll | beam.ParDo(MyDoFn())
        assert_that(output, equal_to([expected_1, expected_2]))
```

### TestStream for Streaming Pipelines
```python
def test_windowed_aggregation():
    with TestPipeline() as p:
        stream = (
            TestStream()
            .advance_watermark_to(0)
            .add_elements([TimestampedValue('a', 1)])
            .add_elements([TimestampedValue('b', 2)])
            .advance_watermark_to(60)  # Close first window
            .add_elements([TimestampedValue('c', 61)])
            .advance_watermark_to_infinity()
        )
        results = p | stream | beam.WindowInto(FixedWindows(60)) | beam.combiners.Count.Globally()
        # Verify per-window outputs
```

### Testing Tips
- Use `DirectRunner` for unit tests. It runs in-process and catches serialization issues.
- Mock external services in `setup()` using dependency injection or environment flags.
- Test DoFn lifecycle: verify `setup()`, `start_bundle()`, `finish_bundle()` are called correctly.
- For side input tests, create side input PCollections with `beam.Create()`.

## Performance Tuning

### Fusion Prevention
Beam fuses adjacent transforms into single stages. This is usually good but can bottleneck when one transform is much slower.

```python
# Insert Reshuffle to break fusion and enable parallelism
slow_input = fast_pcoll | 'BreakFusion' >> beam.Reshuffle()
output = slow_input | 'SlowTransform' >> beam.ParDo(SlowDoFn())
```

### CombinePerKey Over GroupByKey
```python
# Bad: GroupByKey + manual aggregation (shuffles all values per key)
grouped | beam.GroupByKey() | beam.Map(lambda kv: (kv[0], sum(kv[1])))

# Good: CombinePerKey (partial aggregation before shuffle)
pcoll | beam.CombinePerKey(sum)
```

### Reshuffle for Parallelism
```python
# After a source with limited parallelism (e.g., single file)
pcoll | beam.Reshuffle() | beam.ParDo(ProcessDoFn())
```

### Batch External API Calls
```python
class BatchedApiDoFn(beam.DoFn):
    BUFFER = BagStateSpec('buf', PickleCoder())
    TIMER = TimerSpec('flush', TimeDomain.PROCESSING_TIME)
    BATCH_SIZE = 100
    
    def process(self, element, buf=beam.DoFn.StateParam(BUFFER),
                timer=beam.DoFn.TimerParam(TIMER)):
        buf.add(element)
        timer.set(Timestamp.now() + Duration(seconds=5))
    
    @on_timer(TIMER)
    def flush(self, buf=beam.DoFn.StateParam(BUFFER)):
        batch = list(buf.read())
        buf.clear()
        results = api_client.batch_call(batch)
        yield from results
```

### Key Performance Rules
1. Minimize serialization: keep elements small, avoid large nested structures.
2. Use `Combine` over `GroupByKey` whenever aggregation is the goal.
3. Break fusion with `Reshuffle` before I/O-bound or slow transforms.
4. Pre-filter early to reduce downstream data volume.
5. Avoid per-element external calls. Batch with state/timers or use `GroupIntoBatches`.

---

*Sources: [Beam Programming Guide](https://beam.apache.org/documentation/programming-guide/), [Beam Patterns](https://beam.apache.org/documentation/patterns/), [Stateful Processing](https://beam.apache.org/blog/stateful-processing/), [Timely Processing](https://beam.apache.org/blog/timely-processing/), [Multi-Language Pipelines](https://beam.apache.org/documentation/sdks/python-multi-language-pipelines/), [BigQuery Patterns](https://beam.apache.org/documentation/patterns/bigqueryio/)*
