# Portable contract v1

## แยกคำถามกับงาน

| Request | Behavior |
|---|---|
| อธิบายแนวคิด/file/error หรือถาม why/how | ตอบตรง ๆ ไม่บังคับ task/log/test หรือ file mutation |
| อ่าน source เพื่ออธิบายคำถาม | ยังเป็น Q&A หากไม่ได้ขอ persistent investigation/report |
| implement/fix/refactor/test/audit/create/update artifact | งาน: บันทึกและ verify ก่อนปิด |
| คำถามที่สั่งเปลี่ยนกฎ/จำ decision | เปลี่ยนเฉพาะ durable record ที่ขอและตรวจผล |
| คำถามพร้อมสั่งทำ | อธิบายแล้วทำ/บันทึกส่วนที่เป็น action |

## Task packet

## Native mode (default)

ใช้ work-items/<task-id>/BRIEF.md, HANDOFF.md, events.md, VERIFICATION.md และ evidence โดย native host tools ได้ ไม่ต้องติดตั้ง Python/สร้าง JSON gate. ระบุ owner/scope/acceptance และ actual checks. Hash ไม่คำนวณให้ not_computed; unused optional gate = not_run_optional. Native review ไม่ใช่ machine-gate pass

## Automation mode (optional)

ใช้ packet JSON ด้านล่างเมื่อขอ automation หรือโปรเจกต์บังคับ. Existing project requirements take precedence: required schemas/gates เดิมต้องผ่านจริง หรือ pending ห้าม downgrade ไป native เพื่อหลบ

work-items/<task-id>/ มี task.json, BRIEF.md, HANDOFF.md, events.md, verification.json, evidence/. ระบุ goal/authorization, scope, acceptance, dependencies, current baseline และคำสั่งจริง แยก fact/inference/proposal

State: planned → doing → review → done; doing อาจ blocked/handed_off. Handoff ไม่ใช่ done. Integrator ปิดหลัง review + current verification. Gate อ่าน candidate review/done เท่านั้น ไม่แก้ state ให้เอง

## Completion

- Acceptance ครบพร้อมหลักฐาน current source
- Functional, error/negative, regression หลัง final edits. Code ต้อง pass ทั้งสาม. Docs/audit ต้อง functional/error; regression N/A ต้องมีเหตุผลเฉพาะ
- รัน established full suite สำหรับ code หากมี. ไม่มี test command เป็นข้อจำกัด ไม่ใช่ pass; legacy ใช้ disposable harness ที่เหมาะสม
- Native VERIFICATION หรือ automation receipt มี actual command/tool action/environment/exit/assertions/output refs. Current hashes บันทึกเมื่อคำนวณจริง; automation gate ยังบังคับ hashes ตาม schema
- Known failure หรือ required check ที่รันไม่ได้ = ยังไม่ verified; ห้ามอ้าง complete/green
- Gate ผ่าน = packet consistent/ready_for_review. ต้อง review; independent เมื่อมีจริง มิฉะนั้นระบุ self-review
- อัปเดต task handoff/events และให้ coordinator รวม shared summary

อย่าสร้าง tool availability, independent reviewer, test output หรือสิทธิ์ที่ไม่มีจริง. เอกสารไม่อนุญาต deploy/merge/live DB mutation
