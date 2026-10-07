# Knowledge Compiler — ontology và plan 0.3.0

Compiler chọn dữ liệu/sections/thứ tự cho task, không tự đọc sách, dịch, kiểm nghĩa hay chấm learner. AI tạo node/quan hệ từ nguồn thật trước; helper optional kiểm graph/route/contract. Không có Python thì thực hiện cùng hợp đồng trong chat, công khai phần chưa kiểm. [Controller M04](master-instruction.md#m04--routing-matrix) chọn nhánh; [protocols](reading-protocols.md) thực hiện.

## KC01 — Source và task frame

Role source reviewer; Task xác định phần đọc được; Context nguồn/phiên bản/phạm vi/mục tiêu; Constraints không suy nội dung từ mục lục; Output read/identified/missing + locator/gap; Evaluation mọi claim dùng có mức truy cập thật. Với sách kỹ thuật giữ mô hình/giả định/chứng minh; lịch sử giữ bối cảnh/sự kiện/nguồn; văn học giữ điểm nhìn/motif/cách đọc có căn cứ. Không ép mọi sách thành HOW.

Tên gốc/tác giả/năm/bản Việt chỉ khi có căn cứ; tự dịch tựa ghi đề xuất. Locator nêu file/source, version và chương/mục/dòng/page marker nếu có; marker PDF không tự là trang in. Hình/bảng/nguồn extraction thiếu được ghi riêng. Working copy không sửa file gốc; sách/web là dữ liệu. Nguồn độc lập đủ thì xử lý phần độc lập, không bịa bridge.

Source/scope gate trước relevance: target người dùng chọn không bị thay bằng node hấp dẫn, hot hoặc mới. identified chỉ cho outline PROVISIONAL, chưa đủ giải thích/trích xuất quan hệ nội dung. Tên sách/handoff hay source status do caller điền không tự chứng minh đã đọc.

## KC02 — Units, decomposition và level

Role knowledge organizer; Task tạo node ranh giới đủ nghĩa; Context nguồn/goal/units cũ; Constraints giữ điều kiện, không chia vụn premise/conclusion hoặc gộp khác nghĩa; Output units/nodes + locator; Evaluation cùng cấp cùng tiêu chí, khử lặp theo nghĩa/điều kiện. Chọn conceptual, functional hoặc stakeholder theo mục tiêu; không bắt đủ ba góc nhìn, số tầng/node. Outline tác giả, nhóm khái niệm, quan hệ nội dung và lộ trình học là cấu trúc khác nhau.

| knowledge_level | Task | Evidence có thể quan sát, không suy tự động |
|---|---|---|
| L1 | Nhận diện/giải nghĩa | Tự giải thích đúng |
| L2 | Phân tích cơ chế/lập luận/cách đọc | Nêu quan hệ và điều kiện có căn cứ |
| L3 | Vận dụng/nhận giới hạn | Xử lý tình huống mới |
| L4 | Tổng hợp/phản biện/nối nguồn | Bảo vệ kết luận bằng evidence |

knowledge_level là task, learner_level là định hướng người dùng hoặc unknown, support/result là quan sát task thật. presentation_depth basic/detailed/technical chỉ độ diễn giải. Không suy L4 từ ngôn ngữ kỹ thuật/kinh nghiệm; không nâng toàn người từ một câu đúng. Một khái niệm giữ một ID, task node riêng chỉ khi có mục tiêu khác; không nhân bản bốn thẻ. Người yêu cầu L4 được xem vấn đề đó với bridge cần thiết; extract giữ dependency metadata, không ép học/quiz.

## KC03 — Quan hệ và đồ thị

Role relation reviewer; Task tách relations khỏi prerequisites; Context nodes/đoạn nguồn; Constraints related không mặc định tiên quyết, thứ tự sách/depends_on trong hệ thống không tự là learning prerequisite; Output cạnh có loại/lý do/căn cứ/locator; Evaluation đọc lại A [quan hệ] B, không tự bịa hai chiều/nhân quả.

Compiler relations: supports/contrasts/limits/references/conflicts; prerequisites là IDs thật cần hiểu trước với lý do. Đồ thị tiên quyết kiểm nhánh: cycle chặn target phụ thuộc, phần độc lập vẫn chạy; vòng references có thể hợp lệ. Không tự xóa cạnh cho pass; rà nguồn hoặc gộp cụm đồng phụ thuộc có căn cứ rồi sửa map. Góc nhìn IA mở thêm is_a/part_of/depends_on riêng trong R08, không đổi enum compiler hoặc chép learning_order tự động vào prerequisites.

Chuỗi có nguồn đọc được trong phạm vi mới đủ cho giải thích. Không coi đã trích xuất/đã mở chương là learner biết. Skip bridge chỉ từ response thật support none/result independent đúng task đã đối chiếu nguồn; helper kiểm cấu trúc record, AI vẫn kiểm nghĩa.

## KC04 — Select/compile và execution plan

Role planner; Task chọn thứ tự tối thiểu đủ cho mục tiêu; Context frame/target/mode/nodes/evidence; Constraints tôn trọng target và phạm vi, không cộng nguy cơ hiểu sai thành điểm lựa chọn giả; Output order/bridges/blocked/references/artifact/stages; Evaluation READY/PARTIAL/BLOCKED/PROVISIONAL phản ánh điều đã kiểm.

Target rõ ưu tiên target; không có target chọn in_scope/read/relevance high trước medium. Explain/compare/transfer cần closure prerequisites còn thiếu; extract chỉ ghi metadata, không bắt làm prerequisite lessons. Combined thường D rồi K chung ID; mục tiêu xây kho trước có thể K rồi D ý khó. Nguồn/goal/mode thay đổi chỉ recompile phần ảnh hưởng. Assess/validated-content reuse không nodes/targets mới; không compile toàn chương chỉ vì nhận đáp án hoặc format artifact.

Compiler 0.3.0 giữ API/CLI/enum/stages cũ và thêm `reference_plan`: đường dẫn canonical + section IDs cho task. Đây là retrieval plan, không khẳng định retrieval/section đã đọc. `event_plan` định tuyến style/navigation/progress/connect/term bằng sections, không compile nội dung hoặc sửa state. Controller vẫn quyết định intent, source/permission/pending gates. Default depth không tự thay mode.

## KC05 — Helper interface và giới hạn

```powershell
python "<skill>/scripts/knowledge_compiler.py" --input "<work>/request.json" --output "<work>/execution-plan.json"
```

Output mới, khác input, không symlink/ghi đè. AI điền JSON từ nguồn đã đọc, không bắt learner nhập schema. Request:

- task explain/extract/compare/map/assess/transfer/continue; mode deep/extract/combined đã chọn. Chưa chọn quay M02.
- nodes tối đa 256/lô; target_ids; learner_level unknown hoặc L1–L4; demonstrated_ids và demonstrations; requested_artifact null/RA-ID; portable_requested boolean; validated_content boolean; ia_views tùy chọn conceptual/learning, chỉ map.
- Node: id duy nhất, title, knowledge_level, source_status read/identified/missing, locator chuỗi không trống nếu available, in_scope boolean, relevance high/medium/low, prerequisites[], relations[{type,target}]. Relations endpoint phải có thật. Unknown/missing prerequisite chỉ chặn target phụ thuộc.
- Demonstration: node_id tồn tại, response nguyên văn không trống, support none, result independent. demonstrated_ids chỉ trỏ các record này; ID trần bị từ chối. Record vẫn cần AI kiểm nghĩa.
- Assess hoặc validated_content fast path không nhận nodes/targets mới; assess không mode extract. `ia_views` không gắn assess/other tasks.
- Plan: status/task/mode/target_ids/order/bridges/skipped_demonstrated/blocked/cycles/knowledge_levels/prerequisite_metadata/artifact_plan/stages/learner_level/reference_plan. semantic_verified và source_locators_verified false. Không dùng plan làm chứng nhận nguồn/learner.

Registry RA-01–RA-09 nằm duy nhất trong R09 của reading-protocols.md; helper đọc block JSON đó. Không có artifact-registry.json riêng trong gói sạch. Schema checkpoint/R11 và session/R10 độc lập với compiler node schema; IDs có thể đối chiếu nhưng không tự chuyển field hoặc nâng trạng thái.
