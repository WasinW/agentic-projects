# 01 — Part 1: TF Infrastructure

> Terraform ใน `common-data/infrastructure/` + **shared Dataflow base image** ซึ่งเป็น "ของ infra" ตัวจริงที่ common-data แชร์ให้ทุก project

---

## 1. ขอบเขต — common-data แชร์ infra อะไรบ้าง?

ต้องแยกให้ชัด 2 เรื่องที่คนสับสน:

| เรื่อง | จริง ๆ คืออะไร |
|--------|----------------|
| **Terraform *module* กลาง** | ❌ **ไม่ได้อยู่ใน common-data** — อยู่ที่ repo `the1-terraform-gcp` (`gitlab.com/The1central/platform/the1-terraform-gcp`). `common-data/infrastructure/` เป็นแค่ *ผู้ใช้* module นั้น |
| **Shared Dataflow base image** | ✅ **นี่คือของที่ common-data แชร์จริง** — Docker image กลางที่ collector ทุกตัว `FROM` ต่อ เก็บใน Artifact Registry ของ project `the1-common-data-{env}` |

ดังนั้น "Part TF infrastructure" ของ common-data = **infra ที่ใช้ host + provision ตัว base image** เป็นหลัก

---

## 2. โครงสร้าง `infrastructure/`

```
infrastructure/
├── common/GCP/                       ← infra ของ project the1-common-data-{env}
│   ├── main.tf                        backend GCS: prefix "the1-common-data/common/gcp"
│   ├── providers.tf
│   ├── variables.tf                   region, zone, domain
│   ├── terraform.tfvars
│   ├── artifact-registry.tf           ★ สร้าง GAR repo ชื่อ "base-images"
│   └── base-image/dataflow-flex/
│       ├── Dockerfile.flex-base        base image (prod variant)
│       ├── Dockerfile.flex-base-new    base image (stg variant)
│       └── README.md                  คำสั่ง build/push image ด้วยมือ
│
└── common-python-dataflow/           ← infra ของ base image อีกตัว (dataflow-python312-base)
    ├── main.tf                        backend prefix "the1-common-data/services/common-python-dataflow"
    ├── artifact-registry.tf
    ├── variables.tf
    └── terraform.tfvars
```

State ทั้งหมดเก็บที่ bucket `devops-terraformstate-nonprod` แยก prefix:
- `the1-common-data/common/gcp`
- `the1-common-data/services/common-python-dataflow`

---

## 3. `artifact-registry.tf` — หัวใจของ part นี้

ไฟล์ `infrastructure/common/GCP/artifact-registry.tf` สร้าง GAR repo ชื่อ **`base-images`** และที่สำคัญคือมัน
**ให้สิทธิ์ `reader` กับ IAC service account ของทุก domain project** เพื่อให้ทุก repo ดึง base image ไปใช้ได้:

```hcl
module "base_images_repo" {
  count  = terraform.workspace == "stg" ? 1 : 0     # สร้างเฉพาะ workspace stg
  source = "git::https://gitlab.com/The1central/platform/the1-terraform-gcp.git//modules/artifact-registry"

  project_id    = "the1-${var.domain}-${terraform.workspace}"
  repository_id = "base-images"
  format        = "DOCKER"

  reader = [
    "serviceAccount:t1-cat-data-${terraform.workspace}-sa-iac@the1-catalog-data-...",
    "serviceAccount:t1-loy-data-${terraform.workspace}-sa-iac@the1-loyalty-data-...",
    "serviceAccount:t1-gam-data-${terraform.workspace}-sa-iac@the1-gamification-data-...",
    "serviceAccount:t1-mes-data-${terraform.workspace}-sa-iac@the1-messaging-data-...",
    "serviceAccount:t1-par-data-${terraform.workspace}-sa-iac@the1-partner-data-...",
    "serviceAccount:t1-sal-data-${terraform.workspace}-sa-iac@the1-sales-data-...",
    "serviceAccount:t1-ins-${terraform.workspace}-sa-iac@the1-insight-...",
    "serviceAccount:t1-fou-${terraform.workspace}-sa-iac@the1-foundry-...",
    # ... ครบทุก domain (loyalty-insights, martech-insights, crm, discovery, external, commerce)
  ]
}
```

ประเด็นที่ต้องเข้าใจ:
- **`count = ... "stg" ? 1 : 0`** → repo `base-images` ถูกสร้างใน **stg เท่านั้น** (build ที่ stg แล้ว promote ไป prod)
- **`source = "git::https://...the1-terraform-gcp.git//modules/artifact-registry"`** → นี่คือ **กลไก D** (Terraform git module) — common-data ดึง module จาก `the1-terraform-gcp` มาใช้ ไม่ได้เขียน module เอง
- การเพิ่ม domain project ใหม่ → ต้องมาเพิ่ม SA ในลิสต์ `reader` นี้ ไม่งั้น project นั้นจะ pull base image ไม่ได้

---

## 4. Shared Dataflow Base Image — ของที่แชร์จริง

### 4.1 base image คืออะไร / มีกี่ตัว

มี base image กลาง 2 ตระกูล อยู่ในคนละ GAR repo:

| Image | GAR repo | provision โดย | Dockerfile |
|-------|----------|---------------|------------|
| `dataflow-flex-python312-java17` | `the1-common-data-{env}/base-images` | `infrastructure/common/GCP/` | `base-image/dataflow-flex/Dockerfile.flex-base[-new]` |
| `dataflow-python312-base` | `the1-common-data-{env}/dataflow-python312-base` | `infrastructure/common-python-dataflow/` | `common-python-dataflow/Dockerfile.base` |

base image เหล่านี้ = `python312-template-launcher-base` ของ Dataflow + **Java 17 JRE** (จำเป็นสำหรับ Kafka cross-language transform) — ติดตั้งไว้ล่วงหน้าเพื่อให้ collector build เร็วและไม่ต้อง `apt-get install` Java ทุกครั้ง

### 4.2 base image ถูก build อย่างไร

ไฟล์ `common-python-dataflow/dataflow-base-image.gitlab-ci.yml` (include เข้า CI ของ common-data เอง):
- `dataflow-python312-base:terraform:apply:stg/prod` — provision GAR repo (รันเมื่อ `infrastructure/common-python-dataflow/**` เปลี่ยน)
- `dataflow-python312-base:create-image` — Kaniko build จาก `Dockerfile.base` push ขึ้น **stg** (รันเมื่อ `Dockerfile.base` เปลี่ยน)
- `dataflow-python312-base:promote-image:prod` — `crane copy` stg → prod (ไม่ rebuild)

ส่วน `dataflow-flex-python312-java17` — ตาม `base-image/dataflow-flex/README.md` ปัจจุบันยัง **build ด้วยมือ** (มี `docker build`/`push`/`inspect` เขียนไว้ใน README) tag เป็นวันที่ เช่น `:20260416`

### 4.3 consumer ใช้ base image อย่างไร (กลไก consume)

base image ไม่ได้ถูก consume ด้วย terraform — ถูก consume **2 ทาง**:

**(ก) Dockerfile ของ collector `FROM` ต่อ:**
```dockerfile
ARG BASE_IMAGE
FROM ${BASE_IMAGE}
```

**(ข) CI ส่ง `BASE_IMAGE` build-arg เข้าไป:**
- **v2 component** — input `dataflow_base_image_default` (`templates/service-pipeline/template.yml`):
  ```yaml
  dataflow_base_image_default:
    default: "asia-southeast1-docker.pkg.dev/the1-common-data-stg/base-images/dataflow-flex-python312-java17:20260416"
  ```
  job `.common-dataflow-build-image` ส่งค่านี้เป็น `--build-arg BASE_IMAGE=...`
  → **bump ที่เดียว** (input default) ทุก service ที่ใช้ component ก็ได้ image ใหม่
- **legacy repo (gamification, messaging)** — hardcode ใน collector CI:
  ```yaml
  SHARED_BASE_IMAGE_PROJECT: "the1-common-data-stg"
  SHARED_BASE_IMAGE_REPO: "base-images"
  SHARED_BASE_IMAGE_NAME: "dataflow-flex-python312-java17"
  SHARED_BASE_IMAGE_TAG: "20260416"
  ```
  → bump = ต้องไล่แก้ทุก repo ทีละตัว

> หมายเหตุ: build ของ Dataflow ใช้ **NP service account** (`T1_PIPELINE_NP_SA`) ดึง base image จาก `the1-common-data-stg` — เพราะ `reader` ใน `artifact-registry.tf` ให้สิทธิ์เฉพาะ **stg-suffixed IAC SA** (`count` ของ prod = 0). prod image ได้จากการ `crane` promote ไม่ใช่ build ตรง

---

## 5. การเปลี่ยนแปลงในแต่ละ part — checklist

### ถ้าจะ rebuild / bump base image
1. แก้ `Dockerfile.flex-base` / `Dockerfile.base` หรือเปลี่ยน tag วันที่
2. build + push ตาม `base-image/dataflow-flex/README.md` (flex base ยัง manual) หรือ push `Dockerfile.base` (auto ผ่าน CI)
3. promote stg → prod
4. **อัปเดต consumer:**
   - v2 → แก้ input `dataflow_base_image_default` ใน `templates/service-pipeline/template.yml` (จุดเดียว)
   - legacy → ไล่แก้ `SHARED_BASE_IMAGE_TAG` ในทุก collector CI ของ gamification/messaging

### ถ้าจะเพิ่ม domain project ใหม่ให้ pull base image ได้
- เพิ่ม `serviceAccount:...-sa-iac@...` ของ project ใหม่ในลิสต์ `reader` ของ `infrastructure/common/GCP/artifact-registry.tf`
- `terraform apply` ที่ workspace stg

---

## 6. ข้อสังเกต / ความเสี่ยง

- **`count = stg ? 1 : 0`** — `base-images` repo มีเฉพาะ stg ถ้าใครเผลอ apply prod คาดหวัง repo จะงง
- **flex base image ยัง build ด้วยมือ** — ไม่มี CI job (มีแต่ `dataflow-python312-base` ที่ auto) → tag `20260416` อาจหลุด sync กับ Dockerfile
- **tag base image hardcode** ในหลายที่ (README, input default, collector CI legacy) → bump ทีต้องไล่หาหลายจุด
- module Terraform จริงอยู่ `the1-terraform-gcp` — ถ้าจะแก้ logic การสร้าง GAR ต้องไปแก้ที่ repo นั้น ไม่ใช่ common-data

---

ถัดไป: [02 — Dataform](02-dataform.md)
