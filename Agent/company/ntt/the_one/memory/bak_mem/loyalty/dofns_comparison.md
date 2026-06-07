# DoFns Comparison: members vs purchases vs messaging

## Pipeline DoFns (`src/application/pipeline/dofns.py`)

Each collector has its own `dofns.py` with different DoFns:

### members-collector & purchases-collector (same pattern)
```
Kafka raw bytes → ExtractValueDoFn → DecodeParseDoFn → AttachEventNameDoFn → BuildRawEventDoFn
```
- `ExtractValueDoFn`: Extract value bytes from Kafka KV pair
- `DecodeParseDoFn`: Decode bytes → JSON parse
- `AttachEventNameDoFn`: Attach event name derived from Kafka topic name
- `BuildRawEventDoFn`: Build standardized RawEvent dict

### messaging-collector (different pattern)
```
Kafka event (already has eventName) → FilterEventNameDoFn → FilterValidEventFieldsDoFn → BuildRawEventDoFn
```
- `FilterEventNameDoFn`: Filter events by allowed eventName list
- `FilterValidEventFieldsDoFn`: Validate required fields exist
- `BuildRawEventDoFn`: Build standardized RawEvent dict (shared concept)

### Key Difference
- **members/purchases**: Kafka messages are raw — no eventName yet → must ATTACH
- **messaging**: Kafka messages already structured with eventName → must FILTER

### members-collector additional DoFns (separate files)
- `api_dofns.py`: `ExtractMemberIdAndTierCodeDoFn`, `FetchMemberTierDoFn`, `FetchTierMaintenanceDoFn`, `DeduplicatePairsDoFn`, `DeduplicateMemberIdsDoFn`
- `avro_dofn.py`: `DecodeAvroOrJsonDoFn` (Schema Registry support)
- `transform_dofns.py`: `ExtractMemberTierPayloadDoFn`, `ExtractTierMaintenancePayloadDoFn`, `ExtractTierEvent*PayloadDoFn`

### If we need to align with messaging in the future
1. Add `FilterEventNameDoFn` — filter by allowed event names
2. Add `FilterValidEventFieldsDoFn` — validate required fields
3. May replace `AttachEventNameDoFn` if source starts sending eventName in payload
4. `BuildRawEventDoFn` stays (all 3 have it)

*Created: 2026-03-02*
