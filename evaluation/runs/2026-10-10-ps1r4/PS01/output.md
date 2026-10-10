## learner_view

Nguồn đọc: CDH, markers `pages=19-20`, phạm vi chỉ phần **The Prerequisite Mindsets**, không phải toàn sách.

Tác giả đang chuyển từ việc “ai nên tham gia product trio” sang điều kiện nền để áp dụng continuous discovery: không chỉ đổi framework/tool/tactic, mà phải đổi cách nghĩ. Bà nêu rõ có **6 mindsets** cần được nuôi dưỡng để áp dụng các habits trong sách.

Tôi giữ đúng cấu trúc tác giả: 6 mindset tác giả liệt kê trong phạm vi đã đọc, theo tiêu chí “mỗi mindset là một điều kiện tư duy riêng, có định nghĩa/đối lập hoặc hành vi đi kèm trong đoạn nguồn”. Count là **author-stated** vì nguồn viết “There are six mindsets…” ở page 19. Phạm vi chưa chọn: phần “Working Definition of Continuous Discovery” bắt đầu ở page 20 nhưng nằm ngoài scope “mindsets only”.

| ID | Mindset | Unit đủ nghĩa | Locator |
|---|---|---|---|
| K01 | Outcome-oriented | Thành công không nên được định nghĩa bằng output như code hay feature đã ship, mà bằng outcome: giá trị tạo ra cho khách hàng và doanh nghiệp, đo qua impact lên đời sống khách hàng và tăng trưởng/bền vững của business. | p.19 |
| K02 | Customer-centric | Customer-centric đặt khách hàng vào trung tâm: mục đích của business là tạo và phục vụ khách hàng, nên nhu cầu khách hàng phải được nâng lên ngang hàng với nhu cầu business. | p.19-p.20 |
| K03 | Collaborative | Collaborative đòi hỏi từ bỏ mô hình silo/stage-gate, nơi PM quyết, designer thiết kế, engineer code; thay vào đó, team cùng ra quyết định và tận dụng chuyên môn riêng của từng vai trò. | p.20 |
| K04 | Visual | Visual khuyến khích vượt khỏi ngôn ngữ nói/viết để dùng năng lực tư duy không gian: vẽ, externalize thinking, và map những gì team biết. | p.20 |
| K05 | Experimental | Experimental yêu cầu nghĩ như nhà khoa học: nhận diện assumptions và thu thập evidence, kể cả khi team không có nền đào tạo khoa học chính quy. | p.20 |
| K06 | Continuous | Continuous là chuyển từ project mindset sang continuous mindset: discovery không chỉ làm ở đầu dự án, mà được đưa liên tục vào development process để có câu trả lời nhanh cho discovery questions. | p.20 |

Mạch lập luận ngắn: tác giả cho rằng tools/frameworks không tự mở khóa product success nếu mindset không đổi. Sáu mindset này là điều kiện nền để các continuous discovery habits hoạt động: đổi thước đo thành impact, cân bằng customer/business value, ra quyết định cross-functional, dùng biểu diễn trực quan, kiểm giả định bằng evidence, và làm discovery liên tục thay vì theo dự án.

Câu hỏi chờ: Trong 6 mindset này, mindset nào trực tiếp chống lại cách làm “handoff qua stage gates”, và vì sao?

## AUDIT APPENDIX

SC01 SelectionRecord applied:
```json
{
  "selection_id": "SEL-MINDSETS-001",
  "purpose": "giữ cấu trúc tác giả và trích các mindset thành units đủ nghĩa",
  "scope": "CDH pages 19-20, The Prerequisite Mindsets only",
  "basis": "author_explicit",
  "universe_ref": "six mindsets stated by author",
  "criterion": "mỗi member là một mindset tác giả liệt kê trong phạm vi đã đọc, có định nghĩa/đối lập/hành vi đi kèm",
  "members": ["K01", "K02", "K03", "K04", "K05", "K06"],
  "exclusions_or_not_evaluated": "A Working Definition of Continuous Discovery begins on p.20 but is outside requested scope",
  "completeness": "complete_in_verified_scope",
  "count": 6,
  "count_basis": "author_stated",
  "author_count_locator": "p.19: 'There are six mindsets...'"
}
```

SC02 ArgumentRecord applied:
```json
{
  "argument_id": "A-MINDSETS-001",
  "target_unit_ids": ["K01", "K02", "K03", "K04", "K05", "K06"],
  "source_locators": ["p.19", "p.20"],
  "premises": [
    {"id": "P1", "proposition": "Frameworks/tools/methodologies usually require mindset change, not only tactic change.", "basis": "source_explicit", "locator": "p.19"},
    {"id": "P2", "proposition": "The tactics in this book also require cultivated mindsets.", "basis": "source_explicit", "locator": "p.19"}
  ],
  "conclusion": "Six prerequisite mindsets support successful adoption of the book's continuous discovery habits.",
  "conditions": ["scope limited to the author's six listed mindsets on pages 19-20"],
  "exceptions": [],
  "gaps": []
}
```

SC04 evaluator_sidecar for pending question:
```json
{
  "question_id": "Q-MINDSETS-001",
  "target_unit_ids": [{"id": "K03", "revision": 1}],
  "argument_ref": "A-MINDSETS-001",
  "prompt": "Trong 6 mindset này, mindset nào trực tiếp chống lại cách làm “handoff qua stage gates”, và vì sao?",
  "criterion": [
    {
      "claim": "Collaborative mindset rejects the siloed/stage-gate model.",
      "source_locator": "p.20",
      "critical_condition": "Answer should identify Collaborative, not merely mention cross-functional work in general."
    },
    {
      "claim": "The reason is that decisions should be made as a team while leveraging each role's expertise, instead of PM decides/designer designs/engineer codes.",
      "source_locator": "p.20",
      "critical_condition": "Must include the contrast with handoff/stage-gate or role-silo decision flow."
    }
  ],
  "task": "recall",
  "prepared_before_question": true,
  "support_context": "none",
  "validity": "valid_in_current_source_scope",
  "gaps": []
}
```

GateRecords:
```json
[
  {"gate_id": "G-SOURCE", "status": "PASS", "evidence": "pages 19-20 supplied in CASE CONTEXT; no external source used"},
  {"gate_id": "G-UNITS", "status": "PASS", "evidence": "K01-K06 each maps to one author-listed mindset with locator"},
  {"gate_id": "G-SELECTION", "status": "PASS", "evidence": "SC01 records author-stated count, criterion, scope, exclusion"},
  {"gate_id": "G-MEANING", "status": "PASS", "evidence": "units preserve source contrasts: output/outcome, customer/business needs, silo/collaboration, language/spatial thinking, assumption/evidence, project/continuous"},
  {"gate_id": "G-Q", "status": "PASS", "evidence": "one pending question emitted without criterion or answer in learner_view"}
]
```

State delta / transition:
```json
{
  "readiness": "READY",
  "mode": "combined",
  "pending_question": {
    "id": "Q-MINDSETS-001",
    "prompt": "Trong 6 mindset này, mindset nào trực tiếp chống lại cách làm “handoff qua stage gates”, và vì sao?"
  },
  "transition": "WAIT_RESPONSE",
  "state_persisted_to_file": false
}
```