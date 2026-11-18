# Cross-agent workflow · protocol v1

ใช้กับ agent ที่อ่านไฟล์ได้ทุกค่ายผ่านไฟล์กลาง ไม่รับรอง automatic discovery หรือความสามารถเท่ากันทุกโมเดล

1. อ่าน root AGENTS.md → QUICK_CONTEXT.md → HANDOFF.md
2. ถ้าเป็นคำถามขอคำอธิบาย ตอบได้เลย ไม่บังคับ task/log/test
3. งานปกติใช้ native Markdown packet (BRIEF/HANDOFF/events/VERIFICATION + evidence); Automation/required gates ใช้ JSON packet. ยืนยัน owner/scope; ใช้ registry ถ้ามี
4. อ่านเฉพาะ owning source/dependencies ที่จำเป็น ทำงานตาม scope และ checkpoint task-local
5. หลัง final edit รัน functional + error/negative + regression tests ที่เหมาะสม เก็บผลจริงและ current hashes
6. Review native evidence โดยตรง; ถ้าใช้ Automation/โปรเจกต์บังคับ gate ให้รัน verify_task.py ด้วย. ไม่อ้าง native review เป็น machine-gate pass
7. Review/integrate ทีละงาน อัปเดต handoff แล้วคืน ownership

| เรื่อง | เอกสาร |
|---|---|
| คำถาม vs งาน และ completion | CONTRACT.md |
| แบ่งงานไม่ชนกัน | COLLABORATION.md |
| สลับโมเดล/รับช่วงเมื่อ limit | HANDOFF_PROTOCOL.md |
| Verification/error testing | VERIFICATION.md |
| Executable runner/context/benchmark (v0.2) | V02_TOOLS.md |
| Any stack/CSS discovery and source learning (v0.3) | STACK_UNDERSTANDING.md |
| Universal provider handoff (v0.3) | ../adapters/UNIVERSAL_AGENT.md |
| โมเดลเล็กและ context จำกัด | SMALL_MODEL_PLAYBOOK.md |
| Provider adapters/fallback | ../adapters/README.md |
| Packet templates | ../templates/BRIEF.md, task.json, verification.json |
| Project examples | Add a source-backed task slice after inspecting this project |

UTF-8, JSON protocol_version=1, project-relative POSIX paths, timestamps with timezone. กฎกลางอยู่ AGENTS/WORKING_RULES; adapters ไม่ควรแยกกฎอีกชุดที่ขัดกัน
