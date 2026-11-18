# Collaboration and ownership

## Roles (หนึ่ง agent ทำตามลำดับได้)

- Coordinator/integrator: แบ่ง dependencies/paths, owns registry/shared summaries, review integration และปิด task
- Investigator: อ่าน source เฉพาะ scope คืน evidence/unknowns
- Implementer: แก้ assigned paths, ทดสอบ, ทำ receipt/handoff
- Reviewer/verifier: ตรวจ diff/acceptance/failure cases และ rerun checks; ไม่เงียบแก้ไฟล์ทับ implementer

Roles ไม่ใช่ model tiers ที่รับรองได้. งาน authorization/crypto/migration/payment ให้ reviewer ที่เหมาะสมเมื่อมีจริง; หากไม่มี ให้จำกัดงาน/ระบุความเสี่ยง ไม่แสร้งว่า escalate แล้ว

## Single writer

CLAIMS.json เป็น advisory registry ไม่ใช่ OS/distributed lock. Coordinator คนเดียวเขียน; worker ไม่แข่ง self-assign. ก่อนมอบงานตรวจ parent/child overlap ของ paths, dependencies และ current diff. Folder A ชน A/file. Timestamp เก่าไม่ใช่สิทธิ์แย่งงาน

Concurrent code: ใช้ isolated worktrees + แยกความรับผิดชอบเมื่อมีเครื่องมือ. Worktree ไม่แยก DB/service ให้เอง ต้องใช้ per-task fixtures/ports. ไม่มี worktree ให้ disjoint paths + serialized integration; แยกไม่ได้ให้ทำตามลำดับ

Worker ใช้ work-items/<id>/events.md และ HANDOFF.md ของตัวเอง ไม่ append shared log พร้อมกัน. Coordinator รวมลง shared HANDOFF/TASKS/SESSION_LOG/DECISIONS. กติกานี้แทน shared-log แบบ single-agent เมื่อทำ parallel

## Integration / transfer

1. Worker checkpoint diff, commands/output, hashes, limitations; state review
2. Reviewer อ่าน current source/diff และ error-path evidence
3. Coordinator integrate ทีละ task ตรวจ unexpected edits และ integration/suite
4. File ที่เปลี่ยนหลังทดสอบทำให้ receipt stale ต้อง rerun; ไม่ overwrite unknown work เพื่อแก้ conflict
5. ปิด done และ release claim พร้อมเหตุผล เก็บหลักฐาน

ย้าย owner หลังยืนยัน writer เดิมหยุดและ checkpoint ถูกบันทึกแล้ว. Clock expiry แค่สัญญาณตรวจ ไม่ใช่ auto-steal. Independent clones/หลายเครื่องต้องมี explicit reconciliation หรือระบบ lock ภายนอกหากต้องการ atomic coordination จริง
