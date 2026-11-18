# Immediate agent/model switch

## Sender

Checkpoint หลัง meaningful phase และก่อน long operation/หยุด/ใกล้ limit. Task-local HANDOFF ต้องมี goal/constraints, exact source/changed files, acceptance, done/doing/pending, commands+output/environment, failure/decisions/next action. ห้าม chain of thought/secret

Unfinished state=handed_off; owner คงเดิมจน coordinator transfer. Running process ให้บันทึก command/workdir/state และสิทธิ์การหยุด ไม่ส่ง credential ตาม packet

## Receiver ไม่ต้องมี chat history

1. อ่าน AGENTS + QUICK_CONTEXT + task BRIEF/HANDOFF ยืนยัน owner และ current user authorization
2. ตรวจ scoped git status/diff และ current owning source; อย่าเชื่อ stale line numbers/คำอ้าง agent เดิมโดยไม่ดู evidence
3. รัน check เล็กที่เกี่ยวข้องเพื่อยืนยัน environment. ไม่มี tools ให้บอก advisory/read-only ห้ามอ้าง execution
4. ทำต่อ next incomplete step ไม่เริ่มซ้ำจากศูนย์หรือวนลอง blocker เก่าโดยไม่มี evidence ใหม่
5. บันทึก takeover from/to/time/reason; coordinator ย้าย claim; ห้ามแก้พร้อมกัน

## ข้อความส่งต่อ

Read AGENTS.md, AI_KNOWLEDGE/QUICK_CONTEXT.md and work-items/<task-id>/HANDOFF.md. Continue within assigned paths/current authorization. Verify source/evidence, keep task-local checkpoints, run functional/error/regression checks and hand off before stopping. Explanation-only questions require no mandatory log.

Process ถูก kill ทันทีอาจไม่ทัน final checkpoint; incremental records ลดข้อมูลหาย แต่รับประกัน zero-loss ไม่ได้
