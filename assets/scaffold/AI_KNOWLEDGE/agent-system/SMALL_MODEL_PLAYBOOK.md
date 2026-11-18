# Smaller-model / small-context playbook

เป้าคือ reliable bounded work ไม่ใช่คำรับรอง frontier-equivalent reasoning

## Coordinator จัด packet

- หนึ่ง observable goal พร้อม before/after และ acceptance ขนาดเล็ก
- Exact owning source/read order + invariants/dependent interfaces
- Allowed edit paths/non-goals; แบ่ง scope กว้างเป็น vertical slices
- คำสั่ง/version/fixtures/assertions จริงสำหรับ functional/error/regression
- Known failures/settled decisions/unknowns + next step ที่ไม่ต้องอ่าน chat ทั้งหมด

## Worker loop

อ่าน packet → current source → reproduce/baseline → smallest coherent change → targeted tests → error cases → regression/suite → checkpoint → review

เริ่ม QUICK_CONTEXT + packet + relevant files ไม่ใช่โหลดกราฟ/รายงานทั้งหมด. ต้องอ่านเพิ่มให้เลือก dependency ที่จำเป็นและบันทึกเหตุผลย่อ. Test fail ให้ตรวจสาเหตุ ไม่ broad refactor หรือ weaken assertions เพื่อให้เขียว

Escalate/narrow เมื่อข้อกำหนดขัดกัน, permission policy ไม่ทราบ, live migration, crypto/payment invariants เกิน packet. บอกหลักฐาน/decision ที่ขาด; ไม่มีโมเดลที่เก่งกว่าจริงให้ระบุข้อจำกัด

Reviewer ตรวจว่า fresh agent เข้าใจ trigger/behavior จาก packet ได้ไหม, error cases ทดสอบ bad input/failure จริงไหม, outputs ตรง current hashes ไหม, scope ถูกไหม, review independence ระบุตามจริงไหม
