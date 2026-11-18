# Coordination registry

CLAIMS.json เป็น advisory record ที่ coordinator คนเดียวเขียน ไม่ใช่ concurrent lock implementation. Worker ยืนยัน assignment ก่อนแก้. Empty claims ไม่ใช่อนุญาตแก้ทุกอย่าง

บันทึก task_id, owner/session, paths, state, updated_at; ตรวจ parent/child overlap/dependencies ก่อน assign. Shared AGENTS/summaries/manifests/registry integrator เป็น owner; worker ส่ง task-local changes ให้รวม

Model switch ต้องรักษา task ID/evidence และยืนยัน writer เดิมหยุดก่อน transfer. Independent clones/worktrees ไม่ sync registry ให้เอง ต้อง explicit reconciliation เมื่อข้ามเครื่อง
