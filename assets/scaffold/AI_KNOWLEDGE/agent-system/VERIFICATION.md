# Verify / test / error testing หลังทำงานทุกครั้ง

รัน checks หลัง final relevant edit. เลือก executable/version และ assertions ตามงานจริง ไม่ยิง destructive/live tests เพื่อกรอก category

| Work | Functional | Error/negative | Regression |
|---|---|---|---|
| API/validation | response/data change ถูกต้อง | empty/malformed/boundary/auth denied/missing entity/dependency failure | original bug + affected flow + suite |
| Auth/reset | authorized request สำเร็จ | expired/replayed/wrong-user/disabled/missing auth | bypass เดิมยังถูกปฏิเสธ; session/remember ปกติ |
| Payment/stock | invariant ของ transition | repeated request/cross-order/partial write/concurrent change ใน disposable DB | lifecycle/accounting ไม่พัง |
| Upload/import | accepted fixture | wrong type/size/corrupt/missing/resource bound | supported inputs เดิม |
| UI | rendered behavior | keyboard/error/loading/empty/console/network | relevant viewport/neighbor flow |
| Docs/tooling | links/schema/commands/current refs | broken links/invalid packet/stale receipt/path escape fixtures | existing tools/tests; true N/A มีเหตุผล |
| Audit | code evidence/conditions | seek counterevidence/false-positive paths | อย่าเรียก bug-reproduction flags ว่า fixed tests |

## Native mode (default)

ใช้เครื่องมือ/runtime ของโปรเจกต์ที่มีจริง และเก็บ task-local VERIFICATION.md + evidence: functional/error/regression, คำสั่ง/tool action, environment, exit/result, assertion ที่เห็น, ผ่าน/ไม่ผ่าน/ยังไม่รัน และข้อจำกัด. ไม่ต้องมี Python เพื่อบันทึกหรือ review. Hash ที่ไม่คำนวณ = not_computed. Unused optional gate = not_run_optional ไม่ใช่ passed หรือ ready_for_review. Native Markdown review ไม่ใช่ผล machine gate

## Automation mode (optional)

Existing project requirements take precedence. ถ้าโปรเจกต์บังคับ schema/gate เดิม หรือผู้ใช้ขอ automation ให้ใช้ JSON receipt/gate ต่อไป; missing runtime/required check = pending/unverified ห้าม silent downgrade

### Receipt and gate — automation only

ใช้ templates/verification.json: task ID, timestamp/timezone, exact argv/environment/exit, observed assertions และ output refs/digests. Hash deliverables หลังตรวจ. Redact sensitive output ก่อนเก็บและระบุว่าทำ redaction. ไม่เขียนทับ historical evidence ให้ดูเขียว

```powershell
python AI_KNOWLEDGE/tools/verify_task.py --task AI_KNOWLEDGE/work-items/<id>/task.json
```

Gate ตรวจ packet consistency, categories, current file hashes และ evidence digests เท่านั้น ไม่รัน commands ไม่รับรอง origin/semantic correctness ไม่วัด coverage และไม่แทน review. Receipt ที่บันทึกผิดยังอาจผ่านได้; reviewer ต้องอ่าน output/คำยืนยันและ rerun meaningful checks

Exit 0=ready_for_review; 1=blocked contract; 2=unexpected I/O/format error. ไม่ auto merge/deploy/release

Code ต้อง passed functional/error/regression. Docs/audit ไม่ skip functional/error; regression N/A ต้องมีเหตุผลเฉพาะ. failed/blocked/not_run ใด ๆ ปิดงานไม่ได้. Environment ไม่พร้อมให้เก็บ not verified/blocked ไม่อ้างผ่าน

Project commands/runtime must be discovered from the target; do not assume PHP, npm, a test script or a disposable database exists.

Completion gate also requires nonempty BRIEF.md/HANDOFF.md/events.md next to task.json, environment/version and observed_result for every passed check, and receipt time no earlier than task.started_at. Content still needs semantic review.
