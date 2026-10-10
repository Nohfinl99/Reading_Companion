## learner_view

**Ba ý tôi chọn từ đoạn không quy định số**

Tôi chọn 3 ý từ **đoạn không quy định số lượng** để làm bản tóm gọn, theo tiêu chí: mỗi ý phải là một điều kiện giúp so sánh phương án đúng hơn. Đây là lựa chọn do AI tổ chức, không phải “ba nguyên tắc” tác giả nêu.

1. So sánh phải cùng mục tiêu và cùng mốc thời gian.
2. Cần giữ điều kiện nguồn lực khi kết luận lợi ích/phù hợp.
3. Phần chưa biết phải được ghi rõ, thay vì kết luận vượt dữ kiện.

Không chọn trong bản gọn: định nghĩa chi phí cơ hội và vấn đề giá trị khác đơn vị. Hai ý này vẫn thuộc đoạn nguồn, nhưng không nằm trong tiêu chí chọn 3 ý điều kiện so sánh ở trên.

## AUDIT APPENDIX

**SC01 SelectionRecord**

- `selection_id`: `SEL-CASE-001`
- `purpose`: biên tập danh sách gọn từ đoạn không quy định số
- `scope`: CASE CONTEXT, mục “Đoạn không quy định số lượng”
- `basis`: `ai_selection`
- `universe_ref`: 4 mệnh đề trong đoạn không quy định số lượng
- `criterion`: chọn các ý trực tiếp đặt điều kiện để so sánh phương án đúng hơn
- `members`:
  - cùng mục tiêu và mốc thời gian; locator: “So sánh phương án cần cùng mục tiêu và mốc thời gian.”
  - điều kiện nguồn lực; locator: “Một lợi ích có thể phụ thuộc điều kiện nguồn lực…”
  - ghi điều chưa biết; locator: “thiếu dữ kiện về nguồn lực thì chưa kết luận…”
- `exclusions_or_not_evaluated`: chi phí cơ hội; giá trị khác đơn vị cần tiêu chí so sánh
- `completeness`: `partial`
- `count`: 3
- `count_basis`: `derived_after_selection`
- `author_count_locator`: null
- Evidence: CASE CONTEXT nói rõ “Đoạn không quy định số lượng” và “Selection origin AI-organized, scope đoạn không số.”

**GateRecords**

- `G-SOURCE`: PASS  
  Evidence: source supplied entirely in CASE CONTEXT; no external source/tool used.

- `G-SELECTION`: PASS  
  Evidence: final learner_view states scope, selection criterion, AI origin, count basis by wording “Tôi chọn 3 ý…”, and omitted items.

- `G-HEADING`: PASS  
  Evidence: rejected misleading post-title “Ba nguyên tắc của tác giả”; final title is “Ba ý tôi chọn từ đoạn không quy định số,” preserving AI-selection attribution and limited scope.

- `G-MEANING`: PASS  
  Evidence: final items preserve source claims: same goal/time, resource conditions, and unknowns/gaps. No claim that these are author-numbered principles or whole-book principles.

- `G-Q`: NOT_RUN  
  Evidence: no question was created or pending in this invocation.

**state_delta**

- `state_changed`: false
- `pending_question`: none
- `transition`: final edited artifact emitted; no learner assessment or learning outcome generated.