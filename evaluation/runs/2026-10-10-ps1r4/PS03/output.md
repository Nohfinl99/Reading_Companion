## learner_view

Tôi chọn **2 ý từ toàn bộ CASE CONTEXT** để trình bày theo tiêu chí: ưu tiên các ý dễ bị hiểu sai khi so sánh phương án và có thể dùng lại trực tiếp khi ra quyết định. Kho unit vẫn giữ đủ phạm vi; phần dưới chỉ là subset trình bày.

| ID | Ý trình bày | Nguồn |
|---|---|---|
| U02 | Khi so sánh phương án, cần giữ cùng mục tiêu và cùng mốc thời gian; nếu đổi mốc thời gian thì chênh lệch không còn chứng minh phương án tốt hơn trên cùng tiêu chí. | “Đoạn không quy định số lượng”; “Lập luận và giới hạn cho ví dụ” |
| U03 | Chi phí cơ hội là giá trị của phương án thay thế tốt nhất bị bỏ qua, không phải tổng giá trị của mọi phương án bị bỏ qua. | “Đoạn không quy định số lượng” |

Ghi chú phạm vi: nguồn có đoạn nêu **ba quy tắc**, nhưng ba quy tắc đó chỉ thuộc đúng phạm vi đoạn giả định ấy, không phải “ba quy tắc của toàn bộ sách”. Với yêu cầu này, số **2** là giới hạn trình bày do người học yêu cầu, không phải số lượng ý trong nguồn.

## AUDIT APPENDIX

SC00 / Frame:
- mode: extract
- requested_output: trình bày 2 ý; giữ kho unit đủ nghĩa
- source_id: CASE CONTEXT
- access: read trong prompt
- no file persistence; sidecar records emitted in chat

KC02 / Unit inventory retained:
- U01: ba quy tắc chọn phương án gồm xác định mục tiêu, giữ cùng điều kiện so sánh, ghi điều chưa biết; scope chỉ trong đoạn giả định có số tác giả
- U02: so sánh phương án cần cùng mục tiêu, mốc thời gian và điều kiện; chênh lệch chỉ có nghĩa trong phạm vi đó
- U03: chi phí cơ hội là giá trị phương án thay thế tốt nhất bị bỏ qua
- U04: lợi ích có thể phụ thuộc nguồn lực; thiếu dữ kiện nguồn lực thì chưa kết luận phù hợp
- U05: giá trị khác đơn vị cần tiêu chí so sánh, không cộng trực tiếp
- U06: đổi mốc thời gian không chứng minh phương án tốt hơn trên cùng tiêu chí
- U07: chiếc ghế trống có thể hỗ trợ cách đọc về chờ đợi
- U08: kết luận người vắng mặt đã chết chưa có căn cứ trong đoạn truyện

SC01 / SelectionRecord:
- selection_id: SEL-CASE-001
- purpose: trình bày 2 ý theo yêu cầu, không thu hẹp kho unit
- scope: toàn bộ CASE CONTEXT đã đọc
- basis: mixed; user_limit=2, ai_selection chọn thành viên
- criterion: chọn các ý có rủi ro hiểu sai cao khi so sánh phương án và có tính tái dùng trực tiếp
- members:
  - U02; origin=ai_selection; locators: “Đoạn không quy định số lượng”, “Lập luận và giới hạn cho ví dụ”; inclusion_reason: chặn lỗi so sánh lệch mục tiêu/mốc thời gian/điều kiện
  - U03; origin=ai_selection; locator: “Đoạn không quy định số lượng”; inclusion_reason: chặn lỗi cộng tất cả phương án bỏ qua thành chi phí cơ hội
- exclusions_or_not_evaluated: U01, U04, U05, U06, U07, U08 retained in inventory but not presented
- completeness: complete_in_verified_scope
- count: 2
- count_basis: user_limit
- author_count_locator: null for selected count; author-stated count of three applies only to “Đoạn có số tác giả trong nguồn giả định”

GateRecords:
- G-SOURCE: PASS; evidence: all source spans supplied in CASE CONTEXT
- G-UNITS: PASS; evidence: 8 units retained with scoped boundaries
- G-SELECTION: PASS; evidence: selection criterion, origin, count_basis, exclusions, and locators recorded
- G-HEADING: PASS; evidence: learner_view states “2 ý” is user presentation limit, not author/global count
- G-MEANING: PASS; evidence: U02/U03 preserve source conditions and definitions
- G-Q: NOT_RUN; no question generated or answered
- G-EXAMPLE: NOT_RUN; no ExampleLink artifact emitted

state_delta:
- mode_effective: extract
- inventory_created: U01-U08
- presented_selection: SEL-CASE-001
- pending_question: unchanged / none supplied
- learner_response: none
- learning_outcome: none
- transition: READY → handoff in chat; no file saved.