# Seven Peaks — Pre-Interview Answers

---

## Q1: Why are you looking to change your current job?

### แบบเต็ม

ตำแหน่งปัจจุบันเป็น consultant ซึ่งได้เรียนรู้เยอะมาก แต่เหตุผลหลักที่อยากเปลี่ยนคือเรื่อง **working structure**

Scope of Work ถูกระบุไว้ค่อนข้างกว้างตั้งแต่ช่วง presale ทำให้พอเข้า delivery จริง requirements มีการเปลี่ยนแปลงบ่อยภายใต้ timeline เดิม ประกอบกับที่ site ลูกค้าเป็น multi-vendor structure ซึ่งแต่ละฝ่ายมี priority ต่างกัน การ align งานจึงค่อนข้างท้าทาย

สิ่งที่ผมทำเพื่อรับมือคือแบ่งงานเป็น release phases — core requirements ส่งมอบก่อน ส่วนที่นอกเหนือ scope เดิมแยกไปเป็น enhancement phase วิธีนี้ช่วยให้ launch ได้ตาม commitment ในขณะที่ให้เวลา clarify scope ของ enhancement กับลูกค้าอย่างชัดเจน

ด้วยปัญหาที่เกิดขึ้น ทำให้ผมไม่ค่อยมั่นใจว่าโปรเจกต์ต่อไปจะได้ทำในสิ่งที่น่าสนใจจริงๆ หรือไม่ เพราะตัว feature ที่หลากหลายของ data platform นั้นน่าสนใจ แต่ scope ที่ไม่เคลียร์กับความต้องการลูกค้าที่ยังไม่ชัดเจน อาจเป็นปัญหาในการ commitment ระยะยาวได้ จึงอยากมองหาโอกาสใหม่ครับ

### แบบสั้น

งานปัจจุบันเป็น consultant ได้เรียนรู้เยอะ แต่ scope ถูกกำหนดกว้างตั้งแต่ presale ทำให้ requirements เปลี่ยนบ่อยระหว่าง delivery ผมรับมือด้วยการแบ่ง release phases เพื่อให้ส่งมอบได้ตาม commitment แต่มองว่า scope ที่ไม่ชัดเจนตั้งแต่ต้นอาจกระทบคุณภาพงานในระยะยาว จึงมองหาโอกาสใหม่ครับ

---

## Q2: How many years of experience do you have in Data Engineering?

8 ปีครับ (มิ.ย. 2017 – ปัจจุบัน)

---

## Q3: Which databases are you familiar?

SQL Server, PostgreSQL, Hive, BigQuery

---

## Q4: Have you worked with data platforms? If so, which ones?

- **Azure Databricks** — data modeling, schema synchronization, automated testing, RBAC (SCB Data-X, 2 ปี+)
- **GCP (Dataflow + BigQuery + Iceberg)** — 5 production pipelines ทั้ง streaming และ batch (NTT DATA/The 1, ปัจจุบัน)
- **Azure Data Factory / Synapse Analytics** — orchestration และ data integration (SCB Data-X)

---

## Q5: Could you describe your experience working with Databricks?

ใช้ Databricks ที่ SCB Data-X ประมาณ 2 ปี บน Azure ร่วมกับ **PySpark / PySpark SQL** เป็นหลัก:

- ออกแบบ data models และ data validation processes
- สร้าง automated tests ผ่าน **Databricks Workspace API** และ **Data Factory API**
- ออกแบบ schema synchronization เพื่อตรวจจับ schema drift ระหว่าง source databases กับ data warehouse
- ทำ POC migration ไป **Unity Catalog**
- พัฒนา **RBAC** แบ่ง access level ตามทีม (risk, compliance, analytics)
- Performance tuning: broadcast joins, partition pruning, repartitioning, caching intermediate DataFrames

---

## Q6: What data sources did you integrate?

- **Kafka (Confluent Cloud)** — streaming events พร้อม Schema Registry + Avro
- **REST APIs** — loyalty member/tier data, enrichment
- **PostgreSQL** — batch daily incremental
- **Pub/Sub** — streaming customer profile events
- **Cloud Bigtable** — profile lookup สำหรับ enrichment
- **SQL Server, Hive, Teradata** — ETL pipelines (SCB, AIS, DTAC)
- **Web Crawlers** — data gathering (AIS)

---

## Q7: What do you believe is the core business of a consulting firm and what essential mindset is critical for thriving in this field?

Core business คือนำความเชี่ยวชาญเฉพาะทางไปช่วยลูกค้าสร้างสิ่งที่ลูกค้าไม่มีทรัพยากรหรือ know-how ทำเอง สิ่งที่ขายจริงๆ คือ **ความไว้วางใจ** และ **ผลลัพธ์ที่จับต้องได้**

Mindset ที่สำคัญ:
1. **Adaptability** — เข้าสู่ tech stack, domain, และวัฒนธรรมของลูกค้าได้เร็ว
2. **Ownership** — ถึงเป็น consultant ก็ต้องรับผิดชอบ deliverable จนจบเหมือนเป็นคนของลูกค้า
3. **Communication** — ประสานงานกับหลายทีมได้ชัดเจน
4. **Value-driven** — ทุกอย่างต้องตอบโจทย์ business value ของลูกค้า ไม่ใช่แค่เขียน code ให้เสร็จ

---

## Q8: What AI tools are you familiar with, and how have you used them?

ใช้ **Claude Code (Anthropic)** เป็นหลัก เป็น AI coding assistant ที่ช่วย review code, draft unit tests, เขียน documentation, และ refactor code โดยตรวจสอบ output เองทุกครั้งก่อนนำไปใช้จริง

---

## Q9: Please indicate your current salary and expected salary per month?

เงินเดือนที่คาดหวัง **95,000 บาท/เดือน** (สามารถพูดคุยเพิ่มเติมได้)

---

## Q10: Would you be interested in a Permanent role, or a Contractual role, or both?

**Permanent**

---

## Q11: What is your preferred starting date?

สามารถเริ่มงานได้ภายใน **1 เดือน** หลังได้รับ offer
