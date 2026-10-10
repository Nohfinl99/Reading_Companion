## learner_view

**Các ý tôi chọn từ CDH marker21 để áp dụng vào nhịp nghiên cứu đội sản phẩm**

Tôi chọn các ý dưới đây từ phạm vi **Page/marker21** để phục vụ mục tiêu: biến định nghĩa “continuous discovery” thành nhịp làm việc nghiên cứu cho đội sản phẩm. Tiêu chí chọn: ý phải trực tiếp giúp thiết kế cadence nghiên cứu lặp lại, gắn với quyết định sản phẩm hằng ngày, và vẫn giữ đúng điều kiện nguồn nêu.

| ID | Ý áp dụng | Cách đưa vào nhịp đội sản phẩm | Nguồn |
|---|---|---|---|
| CDH21-U01 | Tối thiểu có điểm chạm với khách hàng hằng tuần. | Đặt lịch discovery cố định theo tuần, không để nghiên cứu chỉ diễn ra theo tháng hoặc theo dự án lớn. | CDH marker21 |
| CDH21-U02 | Chính đội xây sản phẩm tham gia nghiên cứu. | Product trio hoặc nhóm trực tiếp làm sản phẩm cần nghe khách hàng đều đặn, thay vì chỉ nhận bản tóm tắt từ bên ngoài. | CDH marker21 |
| CDH21-U03 | Hoạt động nghiên cứu nên nhỏ và lặp lại được. | Chọn các hoạt động nhẹ như phỏng vấn ngắn, kiểm tra giả định, xem lại phản hồi, hoặc test nhanh một câu hỏi cụ thể. | CDH marker21 |
| CDH21-U04 | Discovery phải phục vụ một outcome mong muốn. | Mỗi hoạt động nghiên cứu cần gắn với mục tiêu sản phẩm/kinh doanh rõ ràng, không chỉ “nói chuyện với khách hàng” cho có. | CDH marker21 |
| CDH21-U05 | Mục tiêu là đưa input khách hàng vào các quyết định hằng ngày. | Trước các quyết định về roadmap, ưu tiên, thiết kế hoặc experiment, đội nên hỏi: “Quyết định này đang dựa trên input khách hàng nào?” | CDH marker21 |
| CDH21-U06 | Cadence phải có cấu trúc và bền vững. | Thiết kế nhịp nghiên cứu đủ nhỏ để duy trì tuần qua tuần, thay vì một quy trình nặng khiến đội bỏ cuộc sau vài vòng. | CDH marker21 |

**Cầu nối áp dụng**

Điểm quan trọng không phải là “nghiên cứu nhiều hơn”, mà là đổi nhịp ra quyết định: vì đội sản phẩm ra quyết định mỗi ngày, nguồn lập luận rằng customer input cũng phải đi vào nhịp đó thường xuyên hơn. Vì vậy, ví dụ áp dụng hợp lý là: mỗi tuần đội chọn 1 outcome đang theo đuổi, gom 1-2 câu hỏi quyết định đang còn mơ hồ, rồi dùng một hoạt động nghiên cứu nhỏ để giảm mù mờ trước khi quyết định tiếp.

## AUDIT APPENDIX

**SC00 / Frame**
- mode: `extract`
- goal: áp dụng định nghĩa continuous discovery vào nhịp nghiên cứu đội sản phẩm
- source_scope: `CDH marker21 only`
- requested_output: danh sách ý phù hợp để áp dụng
- readiness: `READY`
- gaps: không có nguồn ngoài marker21; không kiểm currency vì đoạn này là định nghĩa/phương pháp, không có claim sản phẩm hiện hành cần cập nhật.

**SC01 / SelectionRecord**
- selection_id: `SEL-CDH21-APPLY-01`
- purpose: chọn ý áp dụng được vào cadence nghiên cứu của đội sản phẩm
- scope: `CDH marker21`
- basis: `ai_selection`
- universe_ref: các mệnh đề trong định nghĩa và đoạn giải thích ở marker21
- criterion: trực tiếp giúp thiết kế nhịp discovery lặp lại, gắn với quyết định sản phẩm hằng ngày, và giữ điều kiện nguồn
- count: `6`
- count_basis: `derived_after_selection`
- completeness: `complete_in_verified_scope`
- members: `CDH21-U01` đến `CDH21-U06`, tất cả locator `CDH marker21`
- exclusions_or_not_evaluated: không dùng nội dung ngoài marker21; không biến các ý này thành toàn bộ phương pháp của sách.

**SC03 / ExampleLink**
- example_id: `EX-CDH21-CADENCE-01`
- kind: `illustration`
- origin: `ai_created`
- target_unit_ids: `CDH21-U01`, `CDH21-U03`, `CDH21-U04`, `CDH21-U05`, `CDH21-U06`
- scenario: đội chọn weekly outcome, gom câu hỏi quyết định, dùng hoạt động nghiên cứu nhỏ trước quyết định tiếp
- evidence_status: `hypothetical`
- source_limits: ví dụ minh họa cách áp dụng định nghĩa; không phải ví dụ tác giả nêu và không chứng minh hiệu quả thực tế.

**GateRecords**
- `G-FRAME`: `PASS`; output đúng mode extract, đúng scope marker21, đúng mục tiêu áp dụng.
- `G-SOURCE`: `PASS`; chỉ dùng đoạn nguồn được cung cấp tại CDH marker21.
- `G-UNITS`: `PASS`; các unit giữ đủ điều kiện chính: weekly, by product team, small activities, desired outcome, customer input for daily decisions, structured/sustainable cadence.
- `G-SELECTION`: `PASS`; danh sách có tiêu chí chọn, origin, scope, count_basis và giới hạn.
- `G-MEANING`: `PASS`; không gán sai thành “toàn bộ sách”, không thêm kết luận hiệu quả ngoài nguồn.
- `G-HEADING`: `PASS`; heading ghi rõ “ý tôi chọn” từ marker21, không gọi là số nguyên tắc tác giả.
- `G-Q`: `NOT_RUN`; không tạo câu hỏi chờ.
- `G-CURRENCY`: `NOT_RUN`; không có claim hiện hành cần web/current check trong phạm vi này.

**state_delta / transition**
- state_delta: không persist file/state; không tạo pending question.
- transition: `READY -> learner_view delivered`; next_owner: user.