**learner_view**

Mình chưa thể giải thích cơ chế “chuyển dữ kiện phỏng vấn thành bản đồ trong hình Ch4” theo nguồn, vì CASE CONTEXT chỉ có title CDH và TOC “Ch4 Experience map”; chưa có nội dung chương, hình, caption, hay đoạn mô tả quy trình.

Trong mode `extract`, phần có thể giữ lại lúc này là:

| Mục | Trạng thái |
|---|---|
| Target | Cơ chế chuyển dữ kiện phỏng vấn thành bản đồ trong hình Ch4 |
| Nguồn đã có | Title CDH; TOC Ch4 “Experience map” |
| Nguồn còn thiếu | Nội dung Ch4, hình Experience map, caption/legend, đoạn giải thích cách tạo map |
| Kết luận hiện tại | Chưa đủ nguồn để trích unit hoặc giải thích cơ chế |
| Việc cần tiếp theo | Cung cấp đoạn Ch4 hoặc ảnh/hình kèm caption để trích unit có locator |

Danh sách trên là danh sách trạng thái nguồn, không phải danh sách ý chính của chương. Tiêu chí chọn là: chỉ ghi những phần đã nêu trong CASE CONTEXT hoặc phần thiếu ảnh hưởng trực tiếp đến target; chưa suy từ tên chương sang cơ chế.

**AUDIT APPENDIX**

```yaml
artifact_ref: chat_runtime_output
readiness: BLOCKED
next_owner: KC01
state_delta:
  mode: extract
  transition: WAIT_SOURCE
  pending_question: null
  assessment: NOT_RUN

frame:
  goal: "Giải thích cơ chế trong chương/hình này"
  task: "extract/source-gated explanation request"
  mode: extract
  scope: "CASE CONTEXT only"
  target: "cơ chế chuyển dữ kiện phỏng vấn thành bản đồ trong hình Ch4"
  requested_output: "learner_view + audit appendix"
  decisions_known:
    - "Không dùng tools"
    - "Không đọc plugin khác"
    - "Không sửa file"
    - "Nguồn chỉ trong CASE CONTEXT"
  decisions_missing:
    - "Nội dung Ch4"
    - "Hình/caption/legend Experience map"

source_manifest:
  source_id: "CASE_CONTEXT"
  version: unknown
  access_method: "provided in prompt"
  access: "identified/missing"
  accessed_ranges:
    - "Title CDH"
    - "TOC Ch4 Experience map"
  analyzed_ranges:
    - "CASE CONTEXT text"
  missing_ranges:
    - "Chapter 4 body"
    - "Experience map figure"
    - "caption/legend/description of mechanism"
  media_gaps:
    - "Figure not provided"

selection_record_SC01:
  selection_id: "SEL-STATUS-001"
  purpose: "Báo trạng thái nguồn liên quan trực tiếp đến target"
  scope: "CASE CONTEXT"
  basis: "ai_selection"
  universe_ref: "CASE_CONTEXT fields available in prompt"
  criterion: "Chỉ chọn mục đã có trong CASE CONTEXT hoặc mục thiếu chặn trực tiếp target cơ chế Ch4/hình"
  members:
    - ref: "target"
      origin: "user_selection"
      source_locators: ["USER INPUT", "CASE CONTEXT target"]
      inclusion_reason: "Đây là yêu cầu và target đang kiểm"
    - ref: "available_source"
      origin: "ai_selection"
      source_locators: ["CASE CONTEXT"]
      inclusion_reason: "Là phần nguồn duy nhất được cung cấp"
    - ref: "missing_source"
      origin: "ai_selection"
      source_locators: ["CASE CONTEXT: chưa có nội dung chương/hình"]
      inclusion_reason: "Thiếu trực tiếp làm chặn giải thích cơ chế"
  exclusions_or_not_evaluated:
    - "Không đánh giá nội dung Ch4 vì không được cung cấp"
    - "Không suy cơ chế từ TOC/title"
  completeness: "complete_in_verified_scope"
  count: 3
  count_basis: "derived_after_selection"
  author_count_locator: null

gate_records:
  - gate_id: "G-FRAME"
    applicable: true
    status: PASS
    source_spans: ["USER INPUT", "CASE CONTEXT"]
    output_spans: ["learner_view", "audit frame"]
    checks:
      - "mode extract retained"
      - "scope restricted to CASE CONTEXT"
      - "no learner response/outcome generated"
    repair_owner: null
    unresolved: []

  - gate_id: "G-SOURCE"
    applicable: true
    status: PARTIAL
    source_spans: ["CASE CONTEXT"]
    output_spans: ["source_manifest", "learner_view"]
    checks:
      - "title/TOC identified"
      - "chapter body missing"
      - "figure/caption missing"
    repair_owner: "KC01"
    unresolved:
      - "Need source text/image before mechanism can be extracted"

  - gate_id: "G-UNITS"
    applicable: true
    status: NOT_RUN
    source_spans: []
    output_spans: []
    checks:
      - "No chapter/figure content available for unit boundary"
    repair_owner: "KC02/R02"
    unresolved:
      - "No extractable mechanism unit"

  - gate_id: "G-MEANING"
    applicable: true
    status: NOT_RUN
    source_spans: []
    output_spans: []
    checks:
      - "No proposition/premise/conclusion from Ch4 available"
    repair_owner: "R02"
    unresolved:
      - "Mechanism explanation blocked by missing source"

  - gate_id: "G-SELECTION"
    applicable: true
    status: PASS
    source_spans: ["CASE CONTEXT"]
    output_spans: ["selection_record_SC01", "learner_view table"]
    checks:
      - "criterion stated"
      - "origin stated"
      - "count_basis stated"
      - "not evaluated source stated"
    repair_owner: null
    unresolved: []

  - gate_id: "G-Q"
    applicable: false
    status: NOT_RUN
    source_spans: []
    output_spans: []
    checks:
      - "No pending question emitted"
      - "No SC04 criterion/answer exposed"
    repair_owner: null
    unresolved: []

evaluator_sidecar:
  SC04_pending_question: null
  criterion: null
  expected_answer: null
  persistence: "not written; chat-only audit"
```