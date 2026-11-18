# กฎทำงานและส่งต่อ — user requirements

## ข้อยกเว้นสำคัญ: ถามเพื่อเข้าใจ

คำถามอธิบายอย่างเดียว ไม่ต้องสร้าง task/log หรือรันทดสอบ แม้ต้องอ่าน source เพื่ออธิบาย. ถ้าสั่งแก้/ทำ audit/report/artifact หรือเปลี่ยนกฎถาวร เป็นงานที่ต้องบันทึก/verify. ถามพร้อมสั่งทำ ให้บันทึกส่วน action

## เมื่อเป็นงาน

## Native mode (default)

ใช้เครื่องมืออ่าน/ค้นหา/แก้ไฟล์และ runtime ที่ host มีอยู่ ไม่ต้องมี Python เพื่อเริ่มต้น. Task ใช้ BRIEF.md, HANDOFF.md, events.md, VERIFICATION.md และ evidence ได้โดยตรง. บันทึกสิ่งที่ทำจริง/คำสั่ง/environment/result/ข้อจำกัด. Hash ที่ไม่ได้คำนวณ = not_computed; optional gate ที่ไม่รัน = not_run_optional ไม่ใช่ passed. Review หลักฐาน Markdown โดยตรง ไม่อ้างว่าเทียบเท่า machine-gate pass

## Automation mode (optional)

ใช้ JSON task.json/verification.json, hashes และ verify_task.py เมื่อผู้ใช้ขอ automation หรือโปรเจกต์บังคับ. Runtime ต้องพร้อมจริง; required gate ที่รันไม่ได้ต้อง pending/unverified

Existing project requirements take precedence. กฎ/schema/gate เดิมที่บังคับต้องยังทำตาม ไม่เปลี่ยนไป native เพื่อหลบ checks

1. อ่าน root AGENTS + QUICK_CONTEXT + current HANDOFF/task packet
2. ยืนยัน owner/scope/tools/current source. Check freshness ก่อนอ้าง snapshot; ไม่ขยายเข้า sibling sites
3. Native ใช้ BRIEF/HANDOFF/events/VERIFICATION และ evidence; Automation ใช้ task.json/verification.json เพิ่มตาม schema. Preserve existing records
4. Checkpoint หลัง meaningful phase และก่อน long operation/หยุด/ใกล้ limit อย่ารอจนจบแชต
5. หลัง final edits ตรวจ functional, error/negative, regression + relevant suite; บันทึกคำสั่ง/tool action/version/exit/output และ hashes เฉพาะที่คำนวณจริง
6. Rerun หลังแก้ที่กระทบผลทดสอบ. Failed/unrun required checks ห้ามปิดงานหรืออ้าง success
7. Review หลักฐานตาม mode; Automation/โปรเจกต์ที่บังคับ gate ต้อง verify_task.py ผ่านด้วย. Integrator อัปเดต handoff/task board และ release ownership

## Multi-agent ownership

อ่าน agent-system/COLLABORATION.md ถ้ามี; ถ้ายังไม่มี ใช้กฎ ownership ในย่อหน้านี้. Coordinator คนเดียวเขียน shared HANDOFF/SESSION_LOG/TASKS/DECISIONS/CLAIMS; worker เขียน task-local events/HANDOFF. ไม่แข่ง append shared file. Registry เป็น advisory ไม่ใช่ lock จริง ต้อง disjoint scopes/worktrees หรือ serialize. ส่งต่อหลังยืนยัน writer เดิมหยุด ห้าม auto-steal จากเวลา

## Durable record ต้องมี

Goal/current user scope, done/doing/pending ที่แยกชัด, changed paths, exact verification/environment/result/output refs, failure/blocker/attempts, decision/evidence/unknowns, concrete next action และสิทธิ์ที่ยังต้องขอ. ไม่บันทึก hidden reasoning/secret/PII. Automation templates อยู่ templates/ เมื่อมี; Native ใช้หัวข้อ goal/scope/checks/handoff ใน Markdown ได้โดยตรง

## Completion policy

Code ต้อง pass functional/error/regression. Docs/audit ต้อง functional/error; regression N/A ต้องมีเหตุผลเฉพาะ ไม่ใช้ N/A เพื่อหลบ check. Rerun suite ที่มีจริง ไม่สมมติ command. Environment ไม่พร้อมให้ระบุ not verified และค้างงาน. Gate ไม่ยืนยัน semantic correctness จึงต้อง review ตามจริง ไม่ปลอม independent reviewer

Source เปลี่ยนให้ update narrative/mark snapshot stale; ห้ามเปลี่ยนแค่วันที่หรือผลเก่าให้ดูผ่าน. ใช้ source/current user instruction เหนือ historical memory. Process kill อาจขาด final checkpoint ได้ จึง checkpoint เป็นระยะ

รายละเอียดเพิ่มเติมเมื่อไฟล์เหล่านี้มีอยู่: agent-system/CONTRACT.md, VERIFICATION.md และ HANDOFF_PROTOCOL.md
