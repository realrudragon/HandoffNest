# HandoffNest

**v0.5.0 · คลังความรู้โปรเจกต์และระบบส่งต่องานสำหรับ AI agents**

ให้ AI อ่านโปรเจกต์ จัดระเบียบความรู้ บันทึกงาน ตรวจสอบผล และเตรียมให้ AI ตัวอื่นรับช่วงต่อได้ การใช้งานปกติ **ไม่ต้องติดตั้ง Python ไม่ต้องรัน bootstrap และไม่ต้องเลือกโหมดทางเทคนิคเอง** — AI ใช้เครื่องมืออ่าน/แก้ไฟล์ของแอปที่คุณใช้อยู่

[English guide](README.en.md) · [ดาวน์โหลด ZIP](https://github.com/realrudragon/HandoffNest/archive/refs/heads/main.zip)

Repository นี้เป็น **Public** ดาวน์โหลดไฟล์ได้โดยไม่ต้องขอสิทธิ์เข้าถึง

## สารบัญ

[เริ่มเร็ว](#quickstart) · [ติดตั้ง](#install) · [ใช้ครั้งแรก](#first-run) · [ฉบับสมบูรณ์](#complete) · [ไฟล์ที่ได้](#outputs) · [คำสั่งประจำวัน](#daily-use) · [ส่งต่อ AI](#handoff) · [Agents](#agents) · [Stacks](#stacks) · [การตรวจสอบ](#verification) · [แก้ปัญหา](#troubleshooting) · [อัปเดต](#updating) · [ความเป็นส่วนตัว](#privacy) · [ขั้นสูง](#advanced)

<a id="quickstart"></a>
## เริ่มใช้ใน 3 ขั้นตอน

1. **ติดตั้งหรือเปิด skill** ตามหัวข้อถัดไป หากติดตั้งแล้วข้ามขั้นตอนนี้ได้
2. **เปิดโฟลเดอร์โปรเจกต์แอป** ที่ต้องการจัดความรู้ ไม่ใช่โฟลเดอร์ที่เก็บตัว skill
3. **ส่งข้อความนี้ในแชตของโปรเจกต์**

```text
$handoff-nest จัดโครงสร้าง AI ให้โปรเจกต์นี้ โดยยังไม่แก้โค้ดแอป
```

AI จะสำรวจ source สร้างเฉพาะไฟล์ความรู้ที่ยังไม่มี รักษาข้อมูลเดิม และแจ้งสิ่งที่ตรวจสอบได้/ยังไม่ทราบ คุณไม่ต้องเปิด terminal เพื่อรันตัวติดตั้งของ skill

ต้องเป็น host ที่มีสิทธิ์อ่าน/แก้ไฟล์จึงจะสร้างให้ได้ หากเป็นแชตอย่างเดียว AI จะเสนอเนื้อหาให้คัดลอก และระบุว่ายังไม่ได้บันทึกหรือทดสอบจริง

<a id="install"></a>
## ติดตั้งครั้งแรก

### วิธีดาวน์โหลดโดยไม่ใช้คำสั่ง

1. เปิด [HandoffNest บน GitHub](https://github.com/realrudragon/HandoffNest)
2. เลือก **Code → Download ZIP** หรือใช้ลิงก์ดาวน์โหลดด้านบน ตาม [คู่มือ GitHub](https://docs.github.com/en/repositories/working-with-files/using-files/downloading-source-code-archives)
3. แตก ZIP แล้วเปลี่ยนชื่อโฟลเดอร์เป็น `handoff-nest`
4. ตรวจว่ามี `SKILL.md`, `assets/`, `references/` อยู่ภายในโฟลเดอร์เดียวกัน อย่าย้ายเฉพาะ SKILL.md แล้วทิ้งไฟล์ประกอบ
5. ถ้าแอปรองรับการติดตั้ง skill ให้ติดตั้งตามวิธีที่แอปนั้นรองรับ ตำแหน่ง/เมนูต่างกันตาม host จึงไม่มีเส้นทางติดตั้งเดียวที่รับรองทุกแอป

ถ้าต้องการให้ coding agent ช่วยติดตั้ง ให้ส่งโฟลเดอร์ที่แตกไว้และบอก:

```text
ช่วยติดตั้ง skill handoff-nest จากโฟลเดอร์ที่ฉันให้
ตามวิธีที่ host นี้รองรับ รักษาไฟล์เดิม และไม่ติดตั้ง runtime เพิ่ม
ถ้า host ไม่มีระบบ skill ให้ใช้ SKILL.md และไฟล์อ้างอิงจากโฟลเดอร์นี้โดยตรง
```

### ถ้าแอปไม่มีระบบ skill หรือไม่พบชื่อ skill

ใช้คำสั่งอ่านไฟล์โดยตรงแทน ตัวอย่างต่อไปนี้เป็น path สมมติ ให้เปลี่ยนเป็นตำแหน่งของคุณ:

```text
อ่าน C:/Skills/handoff-nest/SKILL.md และไฟล์อ้างอิงที่จำเป็นในโฟลเดอร์เดียวกัน
ใช้ skill นี้กับโปรเจกต์ C:/Projects/my-app
สร้างคลังความรู้ไว้นอก public document root โดยยังไม่แก้โค้ดแอป
```

AI ต้องเข้าถึง path เหล่านั้นได้จริง ถ้า host อ่านไม่ได้ ให้แนบไฟล์ที่จำเป็นหรืออนุญาตผ่านกลไกของ host ห้ามอ้างว่าติดตั้ง/อ่านสำเร็จทั้งที่ยังไม่ได้ทำ

<a id="first-run"></a>
## หลังเรียกครั้งแรก AI ควรทำอะไร

- ตรวจ root โปรเจกต์และอ่านกฎ/งานค้างเดิมก่อน ไม่ขยายไปโปรเจกต์พี่น้องเอง
- อ่าน manifest, entrypoint, routing, modules, config และ CSS/template ที่เกี่ยวข้อง
- สร้างเอกสารพื้นฐานและเติมข้อเท็จจริงจาก source พร้อมจุดที่ยังไม่ทราบ
- บันทึกงาน/ผลตรวจสอบ และเตรียมจุดเริ่มสำหรับ agent ตัวถัดไป
- สรุปว่าไฟล์ใดสร้างหรือรักษาไว้ ตรวจอะไรจริง อะไรยังไม่ได้ตรวจ และควรทำอะไรต่อ

การมีโฟลเดอร์หรือแม่แบบครบอย่างเดียวไม่ใช่การวิเคราะห์เสร็จ หากยังมีเพียง TODO ให้สั่งให้ AI เติมจาก source และระบุข้อจำกัดอย่างชัดเจน

สำหรับเว็บ ให้เก็บ `AI_KNOWLEDGE` นอก `public/`, `public_html/` หรือ document root ที่เสิร์ฟออกเว็บ หากเปิดไว้เฉพาะ document root และไม่มีที่ปลอดภัยที่ได้รับอนุญาต AI ต้องขอตำแหน่งก่อนเขียน

<a id="complete"></a>
## ขอฉบับสมบูรณ์ด้วยข้อความเดียว

```text
$handoff-nest จัดโครงสร้าง AI ฉบับสมบูรณ์ให้โปรเจกต์นี้
อ่าน source แล้วเติมภาพรวม architecture, modules, config, flows และ data model
รวม source map, คำถามที่ยังไม่ทราบ, กฎหลาย agent, การตรวจสอบและ handoff
รักษาไฟล์เดิมและยังไม่แก้โค้ดแอป ใช้เครื่องมือที่มีอยู่ ไม่บังคับติดตั้ง Python
สรุปสิ่งที่อ่านจริง หลักฐาน ผลตรวจสอบ และส่วนที่ยังไม่ verified
```

AI จะขยายเอกสารพื้นฐาน 8 ไฟล์ด้วยแผนผัง/คู่มือเพิ่มเติม 16 ไฟล์ รวมเป็น 24 เอกสารหลัก ไม่รวม AGENTS.md และ task records ที่เกิดระหว่างงาน ดู [ขั้นตอนฉบับสมบูรณ์](references/complete-setup.md)

ทุกหัวข้อควรมีหลักฐานจาก source, unknown พร้อมขั้นตอนตรวจต่อ หรือเหตุผลเฉพาะที่ไม่เกี่ยวข้อง เช่น โปรเจกต์ไม่มีฐานข้อมูล ความครบของหัวข้อไม่ได้รับรองว่าอ่านทุกบรรทัดหรือทดสอบทุก runtime/security path แล้ว

Graphify เป็นตัวเลือก: ถ้ามีเครื่องมือ/กราฟที่เหมาะสมให้ใช้พร้อม provenance ถ้าไม่มีให้ใช้ source map และบันทึกสถานะตามจริง ไม่สร้างกราฟปลอมและไม่หยุดการจัดความรู้พื้นฐานเพราะยังไม่มี Graphify

<a id="outputs"></a>
## ไฟล์ที่ได้และควรเริ่มอ่านตรงไหน

โครงสร้างพื้นฐาน:

```text
my-project/
├── AGENTS.md                         กฎเดิม + pointer ที่ไม่เขียนทับกัน
└── AI_KNOWLEDGE/
    ├── START_HERE.md                  ทางเข้าของ agent ใหม่
    ├── QUICK_CONTEXT.md               สรุปสั้น อ่านเร็ว
    ├── PROJECT.md                     เป้าหมายและภาพรวม
    ├── STACK_MAP.md                   stack และหลักฐานที่ยืนยันได้
    ├── WORKING_RULES.md               กฎบันทึก/ทดสอบ/ส่งต่อ
    ├── HANDOFF.md                     สถานะล่าสุดและขั้นตอนต่อไป
    ├── TASKS.md                       งานและผู้รับผิดชอบ
    └── SETUP.md                       โหมด setup และข้อจำกัดจริง
```

ฉบับสมบูรณ์เพิ่ม:

| ไฟล์ | หน้าที่ |
|---|---|
| ARCHITECTURE.md / MODULES.md | โครงสร้างระบบและความรับผิดชอบแต่ละโมดูล |
| SOURCE_MAP.md | คำถาม/งาน → owning files และลำดับอ่าน |
| CONFIG.md / FLOWS.md / DATA_MODEL.md | config precedence, success/error flows, โครงสร้างข้อมูลที่มีหลักฐาน |
| OPEN_QUESTIONS.md / FINDINGS.md | สิ่งที่ยังไม่รู้และข้อค้นพบที่มีเงื่อนไข/หลักฐาน |
| SESSION_LOG.md / DECISIONS.md / MAINTENANCE.md | ประวัติงาน เหตุผลตัดสินใจ และการดูแลความรู้ |
| GRAPHIFY.md | สถานะ/provenance/ข้อจำกัดของกราฟจริง หรือ pending |
| COLLABORATION.md / HANDOFF_PROTOCOL.md | แบ่งเจ้าของไฟล์และรับช่วงอย่างไม่ชนกัน |
| VERIFICATION.md / NEXT_AGENT_PROMPT.md | ผลตรวจสอบจริงและข้อความพร้อมส่งให้ AI ถัดไป |

ระหว่างทำงาน AI จะสร้าง `work-items/<task-id>/` เพื่อเก็บ BRIEF, HANDOFF, events, VERIFICATION และ evidence ตามขอบเขตงาน โปรเจกต์ที่บังคับ JSON schema/gate เดิมยังต้องทำตามกฎนั้น

<a id="daily-use"></a>
## ตัวอย่างคำสั่งประจำวัน

**ทำงานต่อจากบันทึกล่าสุด**

```text
อ่าน AGENTS.md และ AI_KNOWLEDGE/START_HERE.md
ตรวจ HANDOFF.md กับ TASKS.md แล้วทำขั้นตอนที่ยังไม่เสร็จในขอบเขตที่ฉันมอบหมาย
```

**อัปเดตความรู้หลังแก้โค้ด**

```text
อัปเดต AI_KNOWLEDGE ให้ตรงกับ source ที่เปลี่ยน
รักษาประวัติเดิม แยกสิ่งที่ยืนยันแล้วกับสิ่งที่ยังไม่ทราบ
ตรวจผลกระทบ กรณีผิดพลาด และ regression ก่อนสรุปงาน
```

**เก็บงานก่อนติดลิมิตหรือหยุด**

```text
บันทึก checkpoint และ handoff ตอนนี้
ระบุ goal, owner/scope, done/pending, ไฟล์ที่เปลี่ยน, คำสั่งและผลทดสอบจริง
รวมความล้มเหลว ข้อจำกัด และขั้นตอนถัดไป เพื่อให้ agent ใหม่ทำต่อได้ทันที
```

**ถามเพื่อทำความเข้าใจ**

```text
อธิบาย flow นี้ให้ฉันฟังอย่างง่าย ไม่ต้องแก้ไฟล์
```

คำถามอธิบายอย่างเดียวไม่บังคับ log/test ส่วนคำสั่งที่ให้แก้ไฟล์ สร้างรายงาน ตรวจระบบ หรือเปลี่ยนกฎเป็นงานที่ต้องบันทึกและตรวจสอบ

<a id="handoff"></a>
## เปลี่ยน AI หรือทำงานหลาย agent

ก่อนสลับ ให้ตัวเดิมหยุดเขียนไฟล์และบันทึก checkpoint แล้วส่งข้อความนี้ให้ตัวใหม่:

```text
อ่าน AGENTS.md, AI_KNOWLEDGE/START_HERE.md, QUICK_CONTEXT.md และ HANDOFF.md
จากนั้นอ่าน BRIEF/HANDOFF/VERIFICATION ของ task ที่ได้รับมอบหมาย
ยืนยัน owner/scope และตรวจ source ปัจจุบันก่อนทำต่อ
ใช้หลักฐานเดิมเป็นจุดเริ่ม ไม่อ้างว่าทดสอบผ่านจากคำบอกเล่าเพียงอย่างเดียว
```

หนึ่ง path ควรมีผู้เขียนคนเดียว ตัวประสานงานดูแลเอกสารกลาง คนทำงานเขียนบันทึก task ของตนเอง งานที่ชนกันให้แบ่ง path หรือทำตามลำดับ Registry/ตาราง ownership เป็นข้อตกลง ไม่ใช่ระบบ lock จริง

ถ้าเป็นแชตที่อ่านไฟล์ไม่ได้ ให้แนบเอกสารและ owning-source excerpts ที่จำเป็น ตัวนั้นเสนอ patch/ขั้นตอนต่อได้ แต่ต้องให้ agent ที่มีเครื่องมือและสิทธิ์เป็นผู้บันทึก/รันทดสอบจริง

<a id="agents"></a>
## ใช้กับ agent ตัวไหน

| กลุ่ม | วิธีใช้ |
|---|---|
| Codex / host ที่อ่าน AGENTS.md | เรียก skill หรือให้เริ่มอ่านกฎกับ START_HERE |
| Claude Code / Gemini / Cursor / Copilot | ใช้ระบบ skill/instructions ที่ host รองรับ หรือสั่งอ่าน SKILL.md โดยตรง |
| Host ที่ใช้ DeepSeek / GLM / Kimi / โมเดลอื่น | ใช้กฎ/คลัง/ข้อความ handoff ชุดเดียวกัน โดยดูสิทธิ์อ่าน/เขียน/รันจริง |
| แชตอย่างเดียว | แนบเอกสาร รับข้อเสนอ แล้วส่งให้ผู้มีเครื่องมือดำเนินการต่อ |

มีไฟล์ pointer สำหรับ CLAUDE/GEMINI/Cursor/Copilot ในชุด scaffold เพิ่มเติม แต่ native starter ไม่คัดลอกทุก adapter โดยอัตโนมัติ การค้นพบ instructions ต้องตรวจในแต่ละ host/version ไม่มีการเชื่อม API ติดตั้ง SDK หรือให้สิทธิ์เครื่องมือจากชื่อโมเดล

<a id="stacks"></a>
## ภาษา framework และ CSS

ใช้กระบวนการเดียวกับ PHP/CI3/HMVC/Laravel, JS/TS/React/Next/Vue/Nuxt, Python, Go, Rust, Java/.NET, mobile และ stack อื่น โดยอ่านโปรเจกต์นั้นใหม่ตามหลักฐาน

ชุด automation มี 183 recognition signatures และ 53 กลุ่มภาษา/ไฟล์ รวม HTML/CSS/SCSS พร้อมกฎเพิ่มเติมเองได้ เป็นความสามารถตรวจจับ ไม่ใช่การรับรองความเข้าใจทุก framework/version

สำหรับ CSS/UI ให้ตรวจ imports/build pipeline/layers/tokens/theme และ template authority จริง รักษา assets/design system เดิม ไม่เปลี่ยนไปใช้ framework ที่ AI คุ้นเคยเพียงเพราะไม่รู้จักของเดิม ดู [คู่มืออ่าน stack](assets/scaffold/AI_KNOWLEDGE/agent-system/STACK_UNDERSTANDING.md)

<a id="verification"></a>
## AI ต้องตรวจอะไรและบอกผลอย่างไร

| การตรวจ | ตัวอย่าง |
|---|---|
| Functional | ไฟล์/ลิงก์/source references ถูกต้อง หรือฟีเจอร์ทำงานตาม acceptance |
| Error / negative | input ผิด, missing resource, path ไม่ปลอดภัย, permission denied หรือการรักษาไฟล์เดิม |
| Regression | งานเดิม/ไฟล์/กฎ/source ที่ไม่เกี่ยวข้องยังคงถูกต้อง และ relevant suite ผ่าน |

บันทึกคำสั่งหรือ tool action, environment, ผลที่สังเกตจริง และ evidence แยก `passed`, `failed`, `not_run` หาก required check รันไม่ได้ต้องแสดงว่ายังไม่ verified แยกคุณภาพเอกสาร setup ออกจากการทดสอบระบบแอปจริง

Native review ใช้ Markdown ได้ Hash ที่ไม่ได้คำนวณเป็น `not_computed`; optional JSON gate ที่ไม่ใช้เป็น `not_run_optional` ไม่มีการแสร้งว่า machine gate ผ่าน ถ้าโปรเจกต์มีกฎ/gate เดิมที่บังคับใช้ ต้องยังปฏิบัติตาม

<a id="troubleshooting"></a>
## แก้ปัญหาที่พบบ่อย

| ปัญหา | ทำอย่างไร |
|---|---|
| GitHub เปิดแล้ว 404 / ดาวน์โหลดไม่ได้ | ใช้ลิงก์ HandoffNest ด้านบน ตรวจการเชื่อมต่อและ branch `main`; repository เป็น Public และไม่ต้องส่ง token ในแชต |
| AI ไม่รู้จักชื่อ skill | ตรวจว่า SKILL.md อยู่ตรง root ของโฟลเดอร์ ไม่ซ้อนสองชั้น; ใช้คำสั่งอ่านไฟล์ตรงจากหัวข้อติดตั้ง |
| AI ขอให้ติดตั้ง Python ก่อนเริ่ม | ย้ำให้ใช้ native setup; ถ้าเป็น gate เดิมที่โปรเจกต์บังคับ ให้คง pending และแก้ runtime ตาม scope ห้ามข้ามกฎ |
| AI บอกสร้างไฟล์แต่ไม่พบ | ตรวจ path โปรเจกต์และความสามารถเขียนไฟล์จริง ถ้าเป็นแชตให้ถือเป็นข้อเสนอจนกว่าจะบันทึกจริง |
| AI วิเคราะห์โฟลเดอร์ skill แทนแอป | ระบุ path โปรเจกต์เป้าหมายกับ path skill แยกกัน |
| มีแต่แม่แบบ/TODO | ใช้ prompt ฉบับสมบูรณ์ ขอ source evidence/unknown/next action ในทุกหัวข้อ |
| มีคลังเดิมแล้ว | ให้ตรวจและเติมเฉพาะส่วนที่ขาด ไม่ลบคลัง/ประวัติ/กฎมนุษย์เพื่อเริ่มใหม่ |
| ไม่มี Graphify | ใช้ source map และบันทึก pending/unavailable ตามจริง ไม่ต้องสร้างกราฟปลอม |
| ไม่มีสิทธิ์รันทดสอบ | บันทึก not_run/unverified พร้อมคำสั่งที่ควรรัน และส่งต่อให้ผู้มีเครื่องมือ |
| ใกล้ติดลิมิต | สั่ง checkpoint/handoff แล้วหยุด writer เดิมก่อนให้ตัวใหม่รับช่วง |

<a id="updating"></a>
## อัปเดตหรือย้ายเครื่อง

ดาวน์โหลดตัว skill รุ่นใหม่และใช้วิธีอัปเดตที่ host รองรับ หรือให้ coding agent ตรวจ diff/อัปเดตให้ โดยรักษา local changes ที่ไม่เกี่ยวข้องและสิทธิ์เดิม อย่าแทนที่ `AI_KNOWLEDGE` ของแอปด้วยแม่แบบว่างจากรุ่นใหม่

ย้ายเครื่องให้นำโค้ดโปรเจกต์กับคลังความรู้ที่ตรวจแล้วไปด้วย แล้วติดตั้ง skill ใน host ใหม่ตามวิธีของ host นั้น ตรวจ paths/runtime/permissions ใหม่ก่อนทำงานต่อ ไม่ย้าย credentials/session tokens มากับคลัง

การถอด skill ออกจาก host ไม่ได้เป็นคำสั่งให้ลบคลังโปรเจกต์ หากต้องการเอา pointer/กฎออกให้ตรวจและแก้เฉพาะส่วนที่เกี่ยวข้องโดยรักษาข้อมูลมนุษย์

<a id="privacy"></a>
## ขอบเขตและข้อมูลส่วนตัว

ตัว package มีเฉพาะคำแนะนำ แม่แบบ เครื่องมือเสริมและ tests ไม่มี source/รายงานระบบของโปรเจกต์ผู้ใช้อื่น การวิเคราะห์โปรเจกต์จริงต้องไม่คัดลอกรหัสผ่าน token cookies customer data หรือ hidden reasoning ลงคลัง

เก็บ knowledge นอก public document root และทบทวนก่อนแชร์ การใช้กับบริการ AI อยู่ภายใต้สิทธิ์/นโยบายข้อมูลของ host ที่คุณเลือก skill นี้ไม่ได้สร้าง sandbox หรือเปลี่ยนบริการนั้นให้เป็น offline

การติดตั้ง/อ่านคลังไม่ให้สิทธิ์ deploy, migration, เขียน live DB, เรียก API เสียเงิน, ส่งข้อความ หรือ push Git โดยอัตโนมัติ การเผยแพร่/ให้สิทธิ์ผู้ร่วมงานต้องอยู่ในคำสั่งผู้ใช้ที่ชัดเจน ไม่มีการรับรองความสามารถเท่ากันทุกโมเดล

<a id="advanced"></a>
## เครื่องมือขั้นสูงและคู่มือเพิ่มเติม

ผู้ใช้ปกติข้ามส่วนนี้ได้ Python/helpers เป็นทางเลือกสำหรับ automation หรือ existing required gates เท่านั้น แต่ละเครื่องมือมี runtime requirements ของตัวเอง

| ต้องการ | คู่มือ |
|---|---|
| ขั้นตอน native ปกติ | [native setup](references/native-setup.md) |
| ขั้นตอนฉบับสมบูรณ์ | [complete setup](references/complete-setup.md) |
| bootstrap / hashed context / formal gate / benchmark / maintainer tests | [automation](references/automation.md) |
| คำสั่ง runner/context/benchmark | [tool contracts](assets/scaffold/AI_KNOWLEDGE/agent-system/V02_TOOLS.md) |
| universal handoff / profiles | [agent protocol](assets/scaffold/AI_KNOWLEDGE/adapters/UNIVERSAL_AGENT.md) |
| Graphify | [graph workflow](references/graphify.md) |

Maintainer tests อาจใช้ Python แต่เป็นคนละส่วนกับขั้นตอนใช้งาน native ของผู้ใช้ แยกผล deterministic tests, การลองใช้งานจริงบน host และข้อจำกัดที่ยังไม่ทดสอบเสมอ
