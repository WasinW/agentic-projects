# 03 — Part 3: Dataflow Common Module (`common-python-dataflow`)

> Python library ที่ Beam/Dataflow collector ทุกตัว `import` เข้าไปใช้ — package name: **`common-data-python-dataflow`**

---

## 1. ขอบเขต

`common-python-dataflow/` คือ Python package ที่รวม **Apache Beam adapter** ที่ใช้ซ้ำกันทุก collector
(อ่าน Kafka, เขียน BigQuery / Bigtable / Iceberg) collector ไม่ต้องเขียน I/O เหล่านี้เอง — แค่ประกอบ adapter ใน pipeline

ต่างจาก part อื่นตรงที่ part นี้ถูก share ด้วย **กลไก C (Python git dependency)** — ปลอดภัยที่สุด, pin ด้วย tag

---

## 2. โครงสร้าง

```
common-python-dataflow/
├── pyproject.toml                   package: common-data-python-dataflow
├── Dockerfile / Dockerfile.base     base image ของ Dataflow flex template
├── dataflow-base-image.gitlab-ci.yml
├── config/base.yaml
├── .gitlab-ci.yml                   build/test/release ของ module นี้
└── src/common/beam/
    ├── adapters/
    │   ├── input/
    │   │   ├── kafka_reader/         KafkaReaderAdapter + KafkaReaderConfig
    │   │   │   ├── kafka_reader_adapter.py
    │   │   │   ├── kafka_config.py
    │   │   │   ├── kafka_transforms.py
    │   │   │   ├── avro_deserializer.py    Confluent wire-format / Avro
    │   │   │   └── utils.py
    │   │   └── bigquery/             BigQueryReader (table หรือ SQL mode)
    │   └── output/
    │       ├── bigquery/             BigQueryWriterAdapter (append + CDC upsert/delete)
    │       │   └── README.md          ← มี usage doc ละเอียด
    │       ├── bigtable_writer/       BigtableWriterAdapter
    │       └── gcs/                   GCS BigLake Iceberg writer + BLMS catalog config
    └── testing/                      containers.py (testcontainers) , fakes.py , fixtures.py
```

`tool.hatch` package = `src/common` → import path คือ `common.beam.*`

---

## 3. สิ่งที่ module ให้ — adapter หลัก

### Input adapters
| Adapter | import | ใช้ทำอะไร |
|---------|--------|-----------|
| `KafkaReaderAdapter` | `common.beam.adapters.input.kafka_reader` | `beam.PTransform` อ่าน Kafka → decode (AVRO/JSON/AUTO) → filter; รองรับ SASL/SSL + schema registry |
| `BigQueryReader` | `common.beam.adapters.input.bigquery` | อ่าน BQ ด้วย table mode หรือ SQL query mode |

### Output adapters
| Adapter | import | ใช้ทำอะไร |
|---------|--------|-----------|
| `BigQueryWriterAdapter` | `common.beam.adapters.output.bigquery` | เขียน BQ — **append** หรือ **CDC upsert/delete** (Storage Write API) |
| `BigtableWriterAdapter` | `common.beam.adapters.output.bigtable_writer` | เขียน Bigtable DirectRow |
| GCS BigLake Iceberg writer | `common.beam.adapters.output.gcs` | เขียน Iceberg ผ่าน BLMS REST catalog |

### Testing utilities
`common.beam.testing` — `containers.py` (testcontainers — Kafka/BQ จำลอง), `fakes.py`, `fixtures.py` (pytest fixtures)

### ตัวอย่าง `BigQueryWriterAdapter` (จาก README ของ adapter)
```python
from common.beam.adapters.output.bigquery.bigquery_writer import BigQueryWriterAdapter
from common.beam.adapters.output.bigquery.bigquery_writer_config import BigQueryWriterConfig

config = BigQueryWriterConfig(
    project_id="my-project", dataset_id="refined", table_id="member_tier",
    schema=MEMBER_TIER_SCHEMA,
    upsert=True, primary_key=["memberTierId"],   # CDC mode
    triggering_frequency=60,
)
_ = rows | "WriteUpsert" >> BigQueryWriterAdapter(config)
# ใส่ {"_is_delete": True} ใน row dict → emit DELETE mutation
```

---

## 4. dependency + extras

`pyproject.toml`:
```toml
requires-python = "==3.12.*"
dependencies = ["apache-beam[gcp]==2.72.0", "pydantic==2.12.5", "pyarrow==18.0.0"]

[project.optional-dependencies]
iceberg  = ["apache-beam[hadoop]==2.72.0"]                       # codec สำหรับ Iceberg
kafka    = ["confluent-kafka[avro,schema-registry]==2.14.0"]
pubsub   = ["google-cloud-pubsub==2.36.0"]
bigtable = ["google-cloud-bigtable==2.36.0"]
```
→ consumer เลือก extras ตามที่ใช้ เช่น `common-data-python-dataflow[iceberg,bigtable,kafka]`

มี `[tool.uv] override-dependencies` แก้ CVE (cryptography, orjson, requests) — security pin

---

## 5. consumer ใช้ module นี้อย่างไร — กลไก C

ใน `pyproject.toml` ของ collector:
```toml
[project]
dependencies = ["common-data-python-dataflow"]

[tool.uv.sources]
common-data-python-dataflow = {
  git = "ssh://git@gitlab.com/The1central/The1/the1-data/common-data.git",
  subdirectory = "common-python-dataflow",
  tag = "0.0.64"
}
```
`uv sync` → uv clone git tag นั้น build wheel จาก subdirectory นั้น แล้ว lock SHA ลง `uv.lock`

**สำหรับ local dev** (แก้ module + collector พร้อมกัน) — editable path:
```toml
[tool.uv.sources]
common-data-python-dataflow = { path = "../common-data/common-python-dataflow", editable = true }
```

### consumer ปัจจุบัน + tag
| Consumer | extras | tag |
|----------|--------|-----|
| loyalty-data / members-collector | — | `0.0.23` |
| catalog-data / products-collector | — | `0.0.23` |
| sales-data / sales-collector | — | `0.0.32` |
| gamification-data / account-missions-collector | `[iceberg,bigtable,kafka]` | `0.0.64` |
| messaging-data / messages-collector | `[iceberg,bigtable,kafka,pubsub]` | `0.0.64` |

> tag ห่างกันมาก (`0.0.23` → `0.0.64`) เพราะแต่ละทีม bump คนละเวลา — ไม่มี process บังคับให้ sync

---

## 6. Release & Versioning

- release ของ module = **git tag** บน common-data (เช่น `0.0.64`)
- `pyproject.toml` ของ module เขียน `version = "0.1.0"` (ไม่ตรงกับ tag — ตัวที่ "ของจริง" คือ git tag ที่ consumer pin)
- CI ของ module: `common-python-dataflow/.gitlab-ci.yml` (include เข้า `.gitlab-ci.yml` ของ common-data) — lint/test
- **pin ด้วย tag = แก้ module ไม่กระทบ consumer** จนกว่าเขาจะ bump tag เอง → นี่คือกลไกที่ปลอดภัยที่สุดใน common-data

---

## 7. checklist — ถ้าจะแก้ `common-python-dataflow`

1. แก้ code ใน `src/common/beam/...` + เพิ่ม test ใน `tests/common/beam/...`
2. รัน local: `cd common-python-dataflow && uv sync && uv run poe lint && uv run poe test`
3. export public API ผ่าน `__init__.py` ถ้าเพิ่มของใหม่
4. commit + **สร้าง git tag ใหม่** (เช่น `0.0.65`)
5. แจ้ง/อัปเดต consumer: แก้ `tag` ใน `pyproject.toml` ของ collector ที่ต้องการ → `uv lock` → `uv sync`
6. ⚠️ ของเดิมที่ pin tag เก่าจะ **ไม่เปลี่ยน** — ปลอดภัย แต่ก็แปลว่าต้องไล่ bump เองทีละ repo

> ถ้าแก้แบบ breaking change → ตั้ง tag ใหม่ + แจ้ง consumer อย่า force ให้ของเก่าใช้ tag ที่ขยับ

---

ถัดไป: [04 — Cloud Run common module](04-cloudrun-module.md)
