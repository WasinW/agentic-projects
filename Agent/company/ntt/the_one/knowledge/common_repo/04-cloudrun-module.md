# 04 — Part 4: Cloud Run Common Module (`common-python-cloudrun`)

> Python framework สำหรับ Cloud Run collector (batch + streaming) — package name: **`common-data-python-cloudrun`**

---

## 1. ขอบเขต

`common-python-cloudrun/` คือ **framework** (ไม่ใช่แค่ adapter library) สำหรับ collector ที่รันบน Cloud Run —
ตัวที่ดึง REST API / Kafka แล้วเขียน Iceberg / Pub/Sub แบบ config-driven

ต่างจาก `common-python-dataflow`:
- ตัวนั้น = adapter ของ Apache Beam (collector ต้องเขียน pipeline เอง)
- ตัวนี้ = **framework เต็มตัว** — collector แค่เขียน YAML config + ประกอบ builder dict ใน `main.py` แล้วเรียก `create_app()`

share ด้วย **กลไก C (Python git dependency)** เหมือน Part 3

---

## 2. โครงสร้าง

```
common-python-cloudrun/
├── pyproject.toml                   package: common-data-python-cloudrun
└── src/common_cloudrun/
    ├── ports.py                     Protocol: SourcePort, SinkPort, TransformPort,
    │                                StreamingSourcePort/SinkPort/FilterPort, AuthPort
    ├── data_types.py                DataContainer, Records, PipelineResult, HealthState, SinkResult
    ├── adapters/
    │   ├── input/kafka/             KafkaSourceAdapter (streaming)
    │   └── output/
    │       ├── api_source/          ApiSourceAdapter + ApiAuthAdapter (Keycloak OAuth2, paginated REST)
    │       ├── gcs_iceberg/         IcebergBatchSinkAdapter / IcebergStreamingSinkAdapter
    │       │                        + catalog provider, schema strategy, GCP auth
    │       ├── pubsub/              PubSubSinkAdapter
    │       └── sftp_source/         SftpSourceAdapter
    ├── application/
    │   ├── batch_pipeline.py        BatchPipeline — source → transform → destinations (parallel)
    │   ├── streaming_pipeline.py    StreamingPipeline — poll → filter → sink → flush → ack
    │   ├── api_enrichment_transform.py  enrich record ผ่าน API lookup รอง
    │   ├── builtin_transforms.py    PassthroughTransform
    │   └── streaming_filters.py     PassthroughFilter, FieldEqualsFilter
    └── infrastructure/
        ├── builders.py              build_* + DEFAULT_*_BUILDERS dict
        ├── settings.py / settings_models.py  PipelineSettings (Pydantic + YAML)
        ├── gcp_auth.py , secret_manager.py , gcp_logging.py
```

---

## 3. โมเดลการใช้งาน — config-driven, 3 ขั้น

(จาก `common-python-cloudrun/README.md`) ทุก service ที่ build บน framework นี้ทำเหมือนกัน:

1. **เขียน YAML config** — กำหนด `auth` / `sources` / `sinks` / `pipelines`
2. **ประกอบ builder dict ใน `main.py`** — map type string → adapter constructor
   ```python
   AUTH_BUILDERS = {**DEFAULT_AUTH_BUILDERS}            # keycloak → ApiAuthAdapter
   SOURCE_BUILDERS = {**DEFAULT_SOURCE_BUILDERS}        # rest_api → ApiSourceAdapter
   DESTINATION_BUILDERS = {**DEFAULT_DESTINATION_BUILDERS}  # gcs_iceberg → IcebergBatchSinkAdapter
   TRANSFORM_BUILDERS = {"passthrough": passthrough}
   ```
3. **เรียก `create_app()`** — วน config dispatch ผ่าน builder dict แล้วประกอบทุกอย่าง

→ pipeline shape ทั้งหมดมองเห็นได้ในไฟล์เดียว: `main.py`

**Pipeline mode 2 แบบ** (config `app.pipeline_mode` บังคับระบุ):
- `batch` — `Source.extract()` → `Transform` → destinations หลายตัว (parallel `asyncio.gather`)
- `streaming` — `poll()` → filter → publish ทีละ sink → flush → `acknowledge()`

---

## 4. dependency + extras

```toml
requires-python = "==3.12.*"
dependencies = [
  "fastapi", "uvicorn", "pydantic==2.12.5", "pydantic-settings==2.13.1",
  "pyyaml", "google-cloud-secret-manager", "httpx", ...
]
[project.optional-dependencies]
iceberg = ["pyiceberg[gcsfs,pyiceberg-core]==0.11.0", "pyarrow==18.0.0", "google-auth"]
kafka   = ["confluent-kafka[avro,schema-registry]==2.8.2"]
pubsub  = ["google-cloud-pubsub==2.36.0"]
gcs     = ["google-cloud-storage==3.10.1"]
sftp    = ["paramiko", "python-gnupg"]
```
มี FastAPI ในตัว → collector expose endpoint `/trigger` + `/health` ได้ (Cloud Scheduler เรียก `/trigger`)

---

## 5. consumer ใช้ module นี้อย่างไร — กลไก C

```toml
[project]
dependencies = ["common-data-python-cloudrun"]

[tool.uv.sources]
common-data-python-cloudrun = {
  git = "ssh://git@gitlab.com/The1central/The1/the1-data/common-data.git",
  subdirectory = "common-python-cloudrun",
  tag = "0.0.42"
}
```

### consumer ปัจจุบัน
| Consumer | extras | tag |
|----------|--------|-----|
| partner-data / master-collector | `[iceberg,pubsub,gcs]` | `0.0.42` |

> ปัจจุบัน **partner-data/master-collector เป็น consumer หลักของ module นี้** —
> collector batch ตัวอื่น (gamification master-collector, messaging master-collector) ก็ออกแบบมาในแนวเดียวกัน
> (Cloud Run + `api_source` + `gcs_iceberg`) ให้ verify `pyproject.toml` ของแต่ละตัวว่า pin tag ไหน
> rewards-collector (loyalty) ก็เป็น Cloud Run collector ที่ใช้ pattern นี้

---

## 6. Release & Versioning

- release = git tag บน common-data — README ของ module ระบุรูปแบบ tag เช่น `python-cloudrun-0.0.19`
  (ส่วน consumer ปัจจุบัน pin แบบสั้น `0.0.42` — ให้ยึด tag จริงใน GitLab เป็นหลัก)
- `pyproject.toml` ของ module เขียน `version = "0.0.7"` (เป็น metadata ภายใน — ตัวจริงคือ git tag)
- CI ของ module: `common-python-cloudrun/.gitlab-ci.yml` — lint/test
- pin ด้วย tag → **แก้ module ไม่กระทบ consumer จนกว่าเขา bump เอง** (ปลอดภัยเท่า Part 3)

---

## 7. checklist — ถ้าจะแก้ `common-python-cloudrun`

1. แก้ code ใน `src/common_cloudrun/...` + test ใน `tests/unit/...`
2. local: `cd common-python-cloudrun && uv sync && uv run poe lint && uv run poe test`
3. ถ้าเพิ่ม adapter ใหม่ → เพิ่มใน `DEFAULT_*_BUILDERS` ของ `builders.py` ด้วย ไม่งั้น config dispatch ไม่เจอ
4. ถ้าเพิ่ม config field → แก้ `settings_models.py` (Pydantic model) ด้วย
5. commit + tag ใหม่
6. consumer bump `tag` ใน `pyproject.toml` → `uv lock` → `uv sync`

> framework นี้ถูกออกแบบให้ consumer extend ผ่าน builder dict + Pydantic settings — เวลาแก้ ระวัง
> breaking ของ `ports.py` (Protocol) และ `settings.py` (base config model) เพราะ consumer extend มันโดยตรง

---

ถัดไป: [05 — GitLab CI](05-gitlab-ci.md)
