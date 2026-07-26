# Grafana Alert → Email — User Manual (จับมือทำจากศูนย์)

> เป้าหมาย: ตั้ง alert บน Grafana เมื่อ **Kafka Connect ดับ / reconcile fail** → ส่ง **email** ที่บอก
> **รายละเอียด issue + link ตรงมาที่ alert/dashboard**. เขียนแบบ step-by-step บน Grafana **Unified Alerting**
> (Grafana v9–v11; ถ้า UI เวอร์ชันคุณต่างเล็กน้อย ปรับตามชื่อเมนูใกล้เคียง). 🔒 private KB.
> Env: PROD Prometheus datasource, namespace `nsp-th-p-kafka`. Companion: `grafana-alert-aks-CURATED_20260724.md`.

## 0. ภาพรวม 4 ชิ้นที่ต้องมี (ศัพท์ Grafana)
| ชิ้น | คืออะไร | ทำที่ |
|---|---|---|
| **Dashboard + Panel** | กราฟที่โชว์ metric (ไว้ให้ email deep-link มาหา) | Dashboards |
| **Alert rule** | "ถ้ากราฟเกินเกณฑ์ให้ยิง" (query + condition) | Alerting → Alert rules |
| **Contact point** | "ยิงไปที่ไหน" = email ของคุณ | Alerting → Contact points |
| **Notification policy** | "alert นี้ route ไป contact point ไหน" | Alerting → Notification policies |

ลำดับที่แนะนำ: **สร้าง Dashboard/Panel ก่อน** (เพื่อให้ alert link มาหาได้) → สร้าง Alert rule (ผูก panel) →
Contact point (email) → policy → test.

---

## PART 1 — สร้าง Dashboard + Panel ก่อน (เพื่อให้ email link มาหา)

> ถ้าคุณมี `strimzi-operators.json` dashboard อยู่แล้ว → ข้ามไป "1B: เพิ่ม panel ใน dashboard เดิม"

### 1A. สร้าง dashboard ใหม่ (ถ้ายังไม่มี)
1. ซ้ายมือ → **Dashboards** → **New** → **New dashboard**
2. **+ Add visualization** → เลือก datasource = **Prometheus (PROD)**
3. ตั้งชื่อ dashboard (บนขวา ⚙️ **Settings** → Title = `Kafka Connect Health`) → **Save dashboard** (ไอคอน 💾)

### 1B. เพิ่ม panel "Kafka Connect reconcile failures"
1. ใน dashboard → **Add** → **Visualization**
2. Datasource = **Prometheus (PROD)**
3. ช่อง **Query A** ใส่:
   ```promql
   sum(increase(strimzi_reconciliations_failed_total{kind="KafkaConnect", namespace="nsp-th-p-kafka"}[5m]))
   ```
   > ⚠️ label คือ `namespace` **ไม่ใช่** `kubernetes_namespace` — ผิดตัวเดียว = No Data เงียบๆ
4. ขวามือ **Visualization** เลือก **Time series** (หรือ **Stat** ถ้าอยากได้ตัวเลขใหญ่ๆ)
5. ตั้งชื่อ panel (ขวามือ **Panel options** → Title = `Connect reconcile failures (5m)`)
6. **Apply** (บนขวา) → **Save dashboard**
7. **จำ panel นี้ไว้** — เดี๋ยว alert จะ link มาที่ panel นี้

> เพิ่มอีก panel สำหรับ fallback query (Connect ไม่ ready) ก็ดี — ใช้ query ใน PART 6.

---

## PART 2 — สร้าง Alert Rule

1. ซ้ายมือ → **Alerting** → **Alert rules** → **+ New alert rule**

### 2.1 ตั้งชื่อ + query
2. **Name**: `Kafka Connect reconcile failing (PROD)`
3. section **Define query and alert condition**:
   - **Query A** (datasource Prometheus PROD), แบบ **instant**:
     ```promql
     sum(increase(strimzi_reconciliations_failed_total{kind="KafkaConnect", namespace="nsp-th-p-kafka"}[5m]))
     ```
     > 💡 **ตัด `> 0` ออกจาก query** แล้วไปใส่เป็น threshold แทน (ข้อ 2.2) — จะได้ไม่เจอปัญหา No Data ตอนไม่มี failure

### 2.2 ตั้ง condition (threshold)
4. ในส่วน **Alert condition** (expressions ด้านล่าง query):
   - **B = Reduce**: Function = **Last**, Input = **A** (ยุบ time series เหลือค่าเดียว)
   - **C = Threshold**: Input = **B**, condition = **IS ABOVE `0`**
   - กดปุ่มให้ **C** เป็น **Alert condition** (จุดสีน้ำเงิน "Set as alert condition")
   > = "ถ้าจำนวน reconcile-fail ใน 5 นาที > 0 → firing"

### 2.3 evaluation (ความถี่เช็ค)
5. section **Set evaluation behavior**:
   - **Folder**: สร้าง/เลือก folder เช่น `Kafka Alerts`
   - **Evaluation group**: สร้างใหม่ชื่อ `kafka-1m` → **Evaluation interval** = `1m` (เช็คทุก 1 นาที)
   - **Pending period**: `0s` (ยิงทันที) หรือ `5m` (ต้อง fail ต่อเนื่อง 5 นาทีก่อนยิง = กัน noise) — แนะนำ `5m` สำหรับ prod

### 2.4 labels + annotations (นี่คือส่วนที่ทำให้ email มีรายละเอียด)
6. section **Configure labels and notifications**:
   - **Labels** (ใช้ route + แสดงใน mail): กด **+ Add label**
     - `severity` = `critical`
     - `team` = `data-platform`
     - `component` = `kafka-connect`
7. section **Add annotations** (นี่คือ "เนื้อความ" ที่จะโชว์ใน email):
   - **summary** =
     ```
     Kafka Connect reconcile FAILING in {{ $labels.namespace }}
     ```
   - **description** =
     ```
     KafkaConnect {{ $labels.name }} ({{ $labels.kind }}) in namespace {{ $labels.namespace }} — reconcile-failed count in the last 5m = {{ $values.B }}. Check the Strimzi operator log + Connect pods (kubectl get pods -n {{ $labels.namespace }}).
     ```
     > `{{ $values.B }}` = ค่าจาก Reduce B. `{{ $labels.xxx }}` = label จาก metric.
8. **🔗 Link dashboard and panel** (ปุ่มในหน้านี้ — สำคัญสำหรับ deep-link):
   - กด **Link dashboard and panel** → เลือก dashboard `Kafka Connect Health` → panel `Connect reconcile failures (5m)`
   - Grafana จะใส่ annotation ซ่อน `__dashboardUid__` + `__panelId__` ให้ → **email จะมีปุ่ม link ตรงมาที่ panel นี้อัตโนมัติ**
9. **Save rule and exit** (บนขวา)

---

## PART 3 — Contact Point (email) + template ให้ mail สวย

> คุณ export email ได้แล้ว = มี contact point อยู่แล้ว. ตรงนี้คือ **แต่ง template ให้บอก issue + link**

### 3.1 เช็ค/แก้ contact point เดิม
1. **Alerting** → **Contact points** → เจอ email เดิม → **Edit** (ดินสอ)
2. under **Email** → **Addresses** = เมลคุณ (คั่นหลายอันด้วย `;`)

### 3.2 (ทางลัด — แนะนำ) ปล่อย body เป็น default แต่ใส่ annotation ให้ดี
Grafana **default email template** โชว์ให้อยู่แล้ว: alert name, **summary + description** (จาก PART 2.4),
labels, ค่า values, ปุ่ม **View alert rule**, และ (เพราะเรา link panel) ปุ่ม **Go to dashboard / panel**.
→ **แค่ทำ PART 2.4 + 2.8 ให้ครบ email ก็มีรายละเอียด + link ครบแล้ว** โดยไม่ต้องเขียน template เอง

### 3.3 (ทางลึก — optional) custom subject + body
ถ้าอยากคุม format เอง:
1. **Alerting** → **Contact points** → tab **Notification templates** → **+ New template**
2. Name = `kafka_email` → เนื้อหา:
   ```gotemplate
   {{ define "kafka.subject" }}[{{ .Status | toUpper }}] Kafka Connect issue — {{ .CommonLabels.namespace }}{{ end }}

   {{ define "kafka.body" }}
   {{ range .Alerts }}
   🔴 {{ .Labels.alertname }}  ({{ .Status }})
   Namespace : {{ .Labels.namespace }}
   Resource  : {{ .Labels.kind }}/{{ .Labels.name }}
   Summary   : {{ .Annotations.summary }}
   Detail    : {{ .Annotations.description }}
   Fired at  : {{ .StartsAt }}

   🔗 Panel     : {{ .PanelURL }}
   🔗 Dashboard : {{ .DashboardURL }}
   🔗 Alert rule: {{ .GeneratorURL }}
   {{ end }}
   {{ end }}
   ```
   > `.PanelURL` / `.DashboardURL` จะมีค่าก็ต่อเมื่อ **link panel ใน PART 2.8** แล้ว. `.GeneratorURL` = link มาที่ alert rule เสมอ
3. **Save**
4. กลับไป **Contact points** → email เดิม → **Edit** → เปิด **Optional Email settings**:
   - **Subject** = `{{ template "kafka.subject" . }}`
   - **Message** = `{{ template "kafka.body" . }}`
5. **Save contact point**

---

## PART 4 — Notification Policy (route alert → email)

1. **Alerting** → **Notification policies**
2. ทางง่าย: แก้ **Default policy** → **Default contact point** = email ของคุณ (ครอบทุก alert)
3. ทางเจาะจง (แนะนำ): **+ New nested policy**
   - **Matching labels**: `team = data-platform` (ตรงกับ label ใน PART 2.6)
   - **Contact point** = email ของคุณ
   - (optional) **Group by** = `alertname, namespace`; **Group wait** `30s`, **Group interval** `5m`, **Repeat interval** `4h` (กัน spam)
4. **Save policy**

---

## PART 5 — Test + Verify

1. **Alerting** → **Contact points** → email → **Test** → ส่ง test mail → เช็คว่าได้รับ (subject/body/link)
2. ดู state จริง: **Alerting** → **Alert rules** → rule คุณ → ดู **Normal / Pending / Firing**
3. ลอง trigger จริง (ถ้าปลอดภัย): ทำให้ Connect fail ใน UAT แล้วดู — หรือรอ incident จริง
4. **Silence** ตอน maintenance: **Alerting** → **Silences** → **+ New silence** → match `team=data-platform` → ตั้งเวลา

---

## PART 6 — Query สำรอง + companion alert (แนะนำเพิ่ม)

### 6.1 Fallback: จับ "Connect ไม่ ready / ดับ" ตรงๆ (ตามที่คุณคิดไว้)
ถ้า reconcile-failed ไม่เวิร์ค ใช้ query นี้แทน (Connect resource ที่ไม่ ready):
```promql
strimzi_resources{kind="KafkaConnect"} - strimzi_ready_resources{kind="KafkaConnect"}
```
- threshold **IS ABOVE `0`** = มี Connect resource ที่ไม่ ready
- **ข้อดี**: จับ "ดับ/ไม่พร้อม" ตรงกว่า reconcile-failed (ซึ่งเป็น effect-level)
- ทำ alert rule อีกตัวแบบ PART 2 เปลี่ยนแค่ query A

### 6.2 Companion: operator ตายเงียบ (สำคัญ — reconcile alert จับไม่ได้)
```promql
absent(strimzi_reconciliations_periodical_total{namespace="nsp-th-p-kafka"})
```
- threshold **IS ABOVE `0`** (absent คืนค่า 1 เมื่อ metric หาย = operator ตาย/ไม่ scrape)
- **ทำไมต้องมี**: ถ้า operator pod ตายสนิท metric จะหายไปเลย → `increase()` เงียบ → **ตัวนี้ยังยิงได้**

---

## Appendix — gotcha + troubleshooting
- **label ต้องเป๊ะ**: `namespace` / `exported_namespace` / `kind` / `name` — **ไม่ใช่** `kubernetes_namespace` (ผิด = No Data เงียบ)
- **No Data ตอนปกติ**: ถ้าใช้ `... > 0` ใน query โดยตรง ตอนไม่มี fail จะได้ empty → Grafana งงว่า No Data. **แก้**: ตัด `>0` ออก ใช้ Threshold expression แทน (PART 2.2) + ตั้ง **"Alert state if no data" = OK/Normal** ใน rule settings
- **email ไม่มี link panel**: ต้องกด **Link dashboard and panel** ใน alert rule (PART 2.8) `.PanelURL` ถึงจะมีค่า
- **counter reset**: ถ้า operator restart, counter รีเซ็ต → `increase()` อาจ miss → นี่คือเหตุผลต้องมี companion 6.2
- **Grafana version**: ชื่อเมนูอาจต่างเล็กน้อย (v9 vs v11) — หลักการเดียวกัน (rule → condition → eval → labels/annotations → link panel → contact point → policy)
- **PROD-only**: Grafana เห็นแค่ PROD Prometheus; UAT ต้องขอ endpoint จาก network team (ดู obs synthesis)
