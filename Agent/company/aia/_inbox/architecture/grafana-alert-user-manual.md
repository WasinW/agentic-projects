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

> ⚠️ **verified 2026-07-26:** Grafana ปัจจุบัน (v11/v12) หน้า New alert rule เป็น **stepped wizard 6 step** —
> ทำไล่ตามนี้ (ชื่อ section เก่าอย่าง "Set evaluation behavior" / "Add annotations" **ไม่มีแล้ว**):
> 1) Set alert rule name · 2) Define query and condition · 3) Set folder and labels ·
> 4) Configure alert evaluation behavior · 5) Configure notifications · 6) Configure notification message
> **(annotations + Link dashboard/panel ย้ายไปอยู่ step 6 แล้ว)**

1. ซ้ายมือ → **Alerting** → **Alert rules** → **+ New alert rule**

### Step 1 — Set alert rule name
- **Name**: `Kafka Connect reconcile failing (PROD)`

### Step 2 — Define query and condition
- **Query A** (datasource Prometheus PROD), แบบ **instant**:
  ```promql
  sum by (kind, namespace, name) (increase(strimzi_reconciliations_failed_total{kind="KafkaConnect", namespace="nsp-th-p-kafka"}[5m]))
  ```
  > ⚠️ **ต้องมี `by (kind, namespace, name)`** — ถ้าใช้ `sum(...)` เฉยๆ มัน**ตัด label ทิ้งหมด** → `{{ $labels.namespace }}` ใน mail จะเป็น **[no value]**. `by (...)` = เก็บ label ไว้
  > 💡 **ตัด `> 0` ออกจาก query** แล้วใส่เป็น threshold แทน — กัน No Data ตอนไม่มี failure
- **2 โหมด (refId ต่างกัน — สำคัญตอนใส่ `$values` ใน Step 6):**
  - **Simple mode** (Advanced options = ปิด): มีแค่ **A (query) + C (condition "IS ABOVE 0")** → **ไม่มี B** → ใน annotation ใช้ **`{{ $values.A.Value }}`**
  - **Advanced mode** (เปิด): **A (query) → B (Reduce Last) → C (Threshold IS ABOVE 0)** → ใช้ **`{{ $values.B.Value }}`**
  > 👉 ยึด refId ที่ mail โชว์ในบรรทัด **"Value: A=0, C=1"** — ตัวเลข fail อยู่ที่ **A** (simple) หรือ **B** (advanced). `> 0` ย้ายมาอยู่ที่ Threshold นี่เอง
- กด **Set as alert condition** ที่ **C**

### Step 3 — Set folder and labels
- **Folder**: สร้าง/เลือก `Kafka Alerts`
- **Labels** (ใช้ route + โชว์ใน mail): กด **+ Add label** → `severity=critical` · `team=data-platform` · `component=kafka-connect`

### Step 4 — Configure alert evaluation behavior
- **Evaluation group**: สร้างใหม่ `kafka-1m` → **Evaluation interval** = `1m`
  > ℹ️ **evaluation group = แค่ "เช็คทุกกี่นาที" + รันเรียงกัน** — rule ในกลุ่มเดียวกัน **ไม่ impact logic กัน** (แต่ละ rule query อิสระ). เอา Kafka alert หลายตัวไว้กลุ่มเดียวได้ปลอดภัย. **อย่าสับสนกับ "Group by" ใน Notification policy** (อันนั้น = รวม alert เป็น mail เดียว คนละเรื่อง)
- **Pending period**: `5m` (fail ต่อเนื่อง 5 นาทีก่อนยิง = กัน noise)
- **Configure no data and error handling** → **"Alert state if no data or all values are null"** = **Normal**
  > อย่าเลือก Alerting (จะยิงตอนไม่มี data). ค่านี้เมื่อก่อนชื่อ "OK" — ตอนนี้คือ **Normal**

### Step 5 — Configure notifications
- เลือก **contact point** = email ของคุณ — หรือปล่อยให้ **notification policy** route ตาม label (step 3) ดู PART 4

### Step 6 — Configure notification message (annotations + deep-link)
- **Summary** =
  ```
  🔴 Kafka Connect reconcile FAILED — {{ $labels.namespace }}/{{ $labels.name }} (count={{ $values.A.Value }})
  ```
- **Description** (self-contained — เปิด mail รู้เรื่องเลย ไม่ต้องพึ่ง link) =
  ```
  WHAT : KafkaConnect "{{ $labels.name }}" (kind={{ $labels.kind }}) in namespace {{ $labels.namespace }}
         reconcile-failed count (window) = {{ $values.A.Value }}
  LEVEL: {{ $labels.severity }} | team={{ $labels.team }} | component={{ $labels.component }}

  MEANING: Strimzi operator reconcile ล้มเหลว. สาเหตุที่เจอบ่อย:
    - Connect pod boot ไม่ทัน (plugin/JAR โหลดช้า → readiness timeout 600000ms)
    - CoreDNS/DNS ล่ม (operator resolve ไม่ได้ → createOrUpdate failed)
    - broker/dependency ไม่พร้อม

  INVESTIGATE (copy-paste):
    kubectl get pods -n {{ $labels.namespace }} | grep -i connect
    kubectl get kafkaconnect -n {{ $labels.namespace }}
    kubectl describe kafkaconnect {{ $labels.name }} -n {{ $labels.namespace }}
    kubectl logs deploy/strimzi-cluster-operator -n {{ $labels.namespace }} --tail=100 | grep -iE "reconcil|{{ $labels.name }}|error|timeout|dns"
    kubectl get events -n {{ $labels.namespace }} --sort-by=.lastTimestamp | tail -30

  FIX HINT:
    - boot timeout → bake plugin เข้า image / เพิ่ม pod-ready timeout
    - CoreDNS → escalate infra/network
    - stop+resume = กลบชั่วคราว (ไม่ใช่ fix)
  ```
  > ⚠️ **`$values.A` = simple mode / `$values.B` = advanced mode** (ยึด refId ใน mail บรรทัด "Value:"). ใส่ `.Value` เสมอ. ตัดทศนิยม: `{{ printf "%.0f" $values.A.Value }}`
  > ⚠️ ถ้า `{{ $labels.xxx }}` เป็น **[no value]** = query ไม่ได้ใส่ `by (kind, namespace, name)` (ดู Step 2)
  > 💡 self-contained แบบนี้ = **ไม่ต้องพึ่ง link** (แก้ปัญหา localhost ไปในตัว) — เปิด mail แล้ว copy คำสั่งไป investigate ได้เลย
- **🔗 Link dashboard and panel** (ปุ่มอยู่ใน step 6 นี้ — ไม่ใช่ข้างๆ query): เลือก dashboard `Kafka Connect Health` → panel `Connect reconcile failures (5m)` → Grafana ใส่ annotation `__dashboardUid__`/`__panelId__` ให้ → **email มีปุ่ม link ตรงมา panel อัตโนมัติ** (ทำให้ `.PanelURL`/`.DashboardURL` มีค่า)

**Save rule** (บนขวา)

---

## PART 3 — Contact Point (email) + template ให้ mail สวย

> คุณ export email ได้แล้ว = มี contact point อยู่แล้ว. ตรงนี้คือ **แต่ง template ให้บอก issue + link**

### 3.1 เช็ค/แก้ contact point เดิม
1. **Alerting** → **Contact points** → เจอ email เดิม → **Edit** (ดินสอ)
2. under **Email** → **Addresses** = เมลคุณ (คั่นหลายอันด้วย `;`)

### 3.2 (ทางลัด — แนะนำ) ปล่อย body เป็น default แต่ใส่ annotation ให้ดี
Grafana **default email template** โชว์ให้อยู่แล้ว: alert name, **summary + description** (จาก PART 2.4),
labels, ค่า values, ปุ่ม **View alert rule**, และ (เพราะเรา link panel) ปุ่ม **Go to dashboard / panel**.
→ **แค่ทำ Step 6 (annotations + Link panel) ให้ครบ email ก็มีรายละเอียด + link ครบแล้ว** โดยไม่ต้องเขียน template เอง

### 3.3 (ทางลึก — optional) custom subject + body
ถ้าอยากคุม format เอง:
1. **Alerting** → **Contact points** → tab **Templates** → **+ Add notification template** (เมื่อก่อนชื่อ "Notification templates / New template")
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
   > 📍 **หา "Repeat interval" ไม่เจอ?** อยู่ในนี้ → กด **Edit** ที่ policy → เปิด section **"Timing options"** (พับไว้ default) → เจอ Group wait / Group interval / **Repeat interval**. ถ้าเป็น **nested policy** ต้องติ๊ก **"Override general timings"** ก่อนช่องถึงโผล่ (ไม่งั้น inherit จาก default). **Repeat interval ตั้งที่ policy ไม่ใช่ที่ rule**
2. ทางง่าย: แก้ **Default policy** → **Default contact point** = email ของคุณ (ครอบทุก alert)
3. ทางเจาะจง (แนะนำ): **+ New nested policy**
   - **Matching labels**: `team = data-platform` (ตรงกับ label ใน PART 2.6)
   - **Contact point** = email ของคุณ
   - (optional) **Group by** = `alertname, namespace`; **Group wait** `30s`, **Group interval** `5m`, **Repeat interval** `4h` (กัน spam)
4. **Save policy**

### 4.1 อยากได้ "ส่ง mail ครั้งเดียวหลัง fail" (ไม่ spam)
Grafana ส่ง mail ตอนเข้า **Firing** ครั้งแรก แล้ว **ส่งซ้ำทุก "Repeat interval"** ตราบใดที่ยัง firing → ตั้ง 3 อย่างนี้:
| ตั้งที่ | ค่า | ผล |
|---|---|---|
| **Pending period** (Step 4 ของ rule) | `0s` | ยิงทันทีที่ fail |
| **Repeat interval** (policy นี้) | `4h`+ | ระหว่าง firing ไม่ส่งซ้ำถี่ |
| **Disable resolved message** (Email contact point → Optional settings) | ✅ | ไม่ส่ง "หายแล้ว" mail → เหลือแค่ mail ตอน fail |

- เพราะ query ใช้ `increase(...[5m])` → หลัง fail มันจะ >0 อยู่ ~5 นาที แล้วตกกลับ 0 เอง → firing สั้นๆ → **1 fail = 1 mail** (Repeat 4h > 5m เลยไม่ทันส่งซ้ำ)
- fail รัวๆ (crash loop) → firing ค้างยาว = **ยังได้ mail เดียวต่อ incident** (จะซ้ำก็ต่อเมื่อค้างเกิน 4h)

### 4.2 (TRIAL) ส่ง mail ทุกๆ X ชม. ดู status — แม้ยังไม่พัง (heartbeat)
ช่วงแรกอยากเห็น mail เรื่อยๆ เพื่อเช็คว่า format/alert ทำงาน (ไม่ต้องรอให้พังจริง) → ทำให้ **firing ตลอด** + repeat:
| ตั้งที่ | Phase A (ทุก 1h) | Phase B (4-12h) | Phase C = real design |
|---|---|---|---|
| Threshold C | **IS ABOVE `-1`** (จริงเสมอ) | IS ABOVE `-1` | **IS ABOVE `0`** (พังจริงเท่านั้น) |
| Repeat interval | `1h` | `4h`–`12h` | `4h`+ |
| Pending period | `0s` | `0s` | `0s` |
| Disable resolved | — | — | ✅ |
- Description ใส่ `{{ $values.B.Value }}` → mail บอก "failures ตอนนี้ = 0/N" ทุกครั้ง (แนะนำเปลี่ยน query window เป็น `[1h]` ให้ตรง cadence)
- ⚠️ **`IS ABOVE -1` (always-firing) = trial เท่านั้น** (แดงตลอด) → พอมั่นใจ format แล้ว **สลับกลับ Phase C (`IS ABOVE 0`)** อย่าทิ้งไว้ (จะชินชา ignore)

---

## PART 5 — Test + Verify

1. **Alerting** → **Contact points** → email → **Test** → ส่ง test mail → เช็คว่าได้รับ (subject/body/link)
2. ดู state จริง: **Alerting** → **Alert rules** → rule คุณ → ดู **Normal / Pending / Firing**
3. ลอง trigger จริง (ถ้าปลอดภัย): ทำให้ Connect fail ใน UAT แล้วดู — หรือรอ incident จริง
4. **Silence** ตอน maintenance: **Alerting** → **Silences** → **+ New silence** → match `team=data-platform` → ตั้งเวลา

---

## PART 6 — Query สำรอง + companion alert (แนะนำเพิ่ม)

### 6.1 Fallback: จับ "Connect ไม่ ready / ดับ" ตรงๆ (ตามที่คุณคิดไว้)
> ⚠️ **verified 2026-07-26 แก้ query:** `strimzi_ready_resources` **ไม่มีจริง** (metric นี้ไม่มีใน Strimzi).
> metric ที่ถูกคือ **`strimzi_resource_state`** (ค่า 1=ready, 0=not-ready ต่อ resource).
```promql
count(strimzi_resource_state{kind="KafkaConnect"} == 0)
```
- threshold **IS ABOVE `0`** = มี Connect resource ที่ไม่ ready
- (หรือดูรายตัว: `strimzi_resource_state{kind="KafkaConnect"} == 0`)
- **ข้อดี**: จับ "ดับ/ไม่พร้อม" ตรงกว่า reconcile-failed (ซึ่งเป็น effect-level)
- ทำ alert rule อีกตัวแบบ PART 2 เปลี่ยนแค่ query A

### 6.2 Companion: operator ตายเงียบ (สำคัญ — reconcile alert จับไม่ได้)
```promql
absent(strimzi_reconciliations_periodical_total{namespace="nsp-th-p-kafka"})
```
- threshold **IS ABOVE `0`** (absent คืนค่า 1 เมื่อ metric หาย = operator ตาย/ไม่ scrape)
- **ทำไมต้องมี**: ถ้า operator pod ตายสนิท metric จะหายไปเลย → `increase()` เงียบ → **ตัวนี้ยังยิงได้**

### 6.3 ⚠️ Strimzi operator metrics = deprecated (วางแผน migrate)
- **`strimzi_*` operator metrics (reconciliations, resource_state) ถูก deprecate ตั้งแต่ Strimzi 0.48.0 และ ถูกลบใน 0.51.0** → หลัง operator upgrade alert พวกนี้จะ **เงียบเงียบ (No Data)**
- long-term = ย้ายไป **kube-state-metrics** (`kube_pod_status_ready` / `kube_pod_container_status_restarts_total`) — ตรงกับ Phase 4 ใน `observability-synthesis.md`
- interim ใช้ `strimzi_*` ไปก่อนได้ แต่ **เช็ค Strimzi version + ตั้ง reminder** ว่าจะ migrate ก่อน upgrade ข้าม 0.51

---

## Appendix — gotcha + troubleshooting
- **`[no value]` ใน mail — 2 สาเหตุ:** (a) `{{ $labels.x }}` ว่าง = query ใช้ `sum(...)` เฉยๆ ตัด label ทิ้ง → ใส่ `sum by (kind, namespace, name) (...)`; (b) `{{ $values.B.Value }}` ว่าง = คุณอยู่ **simple mode** (ไม่มี refId B) → ใช้ **`$values.A.Value`** (ยึด refId ใน mail บรรทัด "Value:")
- **link เป็น `localhost:3000` เข้าไม่ได้:** Grafana ไม่ได้ตั้ง `root_url` → default localhost.
  - **แก้ถาวร (proper):** `grafana.ini [server] root_url = https://<domain>/` (หรือ env `GF_SERVER_ROOT_URL`) → **แก้ config + restart Grafana** (ไม่ใช่ rebuild; ใน K8s = แก้ ConfigMap/Helm/env → `kubectl apply` → pod restart). **แก้ผ่าน GUI ไม่ได้** (startup config). งาน admin/infra; กระทบทุก link ที่ Grafana สร้าง
  - **workaround (ไม่รอ admin):** (1) ทำ email **self-contained** — ยัด namespace/name/value + คำสั่ง `kubectl` ลง Description ให้ครบ ไม่ต้องพึ่ง link; (2) ถ้ารู้ URL จริงของ Grafana → **Add custom annotation** ใส่ full URL hardcode เช่น `dashboard_link = https://<domain-จริง>/d/<uid>` (bypass root_url เฉพาะ link นั้น)
  - **log ใส่ใน mail ตรงๆ ไม่ได้** (alert นี้ query Prometheus = metric ไม่มี log) → ใส่คำสั่งไปดึง log แทน (`kubectl logs ...`)
- **email มี Value/Labels/Source/Silence เยอะ = default template ของ Grafana เอง** (ไม่ใช่ custom ที่คุณตั้ง) — ปกติ. อยากสั้น/สะอาด → ทำ custom notification template (PART 3.3)
- **label ต้องเป๊ะ**: `namespace` / `exported_namespace` / `kind` / `name` — **ไม่ใช่** `kubernetes_namespace` (ผิด = No Data เงียบ)
- **No Data ตอนปกติ**: ถ้าใช้ `... > 0` ใน query โดยตรง ตอนไม่มี fail จะได้ empty → No Data. **แก้**: ตัด `>0` ออก ใช้ Threshold expression (Step 2) + ตั้งใน **Step 4 → "Configure no data and error handling" → "Alert state if no data or all values are null" = Normal** (ค่าเก่าชื่อ "OK")
- **email ไม่มี link panel**: ต้องกด **Link dashboard and panel** ใน **Step 6** ก่อน `.PanelURL` ถึงจะมีค่า
- **counter reset**: ถ้า operator restart, counter รีเซ็ต → `increase()` อาจ miss → นี่คือเหตุผลต้องมี companion 6.2
- **Grafana version**: ชื่อเมนูอาจต่างเล็กน้อย (v9 vs v11) — หลักการเดียวกัน (rule → condition → eval → labels/annotations → link panel → contact point → policy)
- **PROD-only**: Grafana เห็นแค่ PROD Prometheus; UAT ต้องขอ endpoint จาก network team (ดู obs synthesis)
