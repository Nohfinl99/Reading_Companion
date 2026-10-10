# Knowledge Compiler — ontology và plan 0.3.0

Compiler chọn dữ liệu/sections/thứ tự cho task, không tự đọc sách, dịch, kiểm nghĩa hay chấm learner. AI tạo node/quan hệ từ nguồn thật trước; helper optional kiểm graph/route/contract. Không có Python thì thực hiện cùng hợp đồng trong chat, công khai phần chưa kiểm. [Controller M04](master-instruction.md#m04--routing-matrix) chọn nhánh; [protocols](reading-protocols.md) thực hiện.

## KC01 — Source và task frame

Role source reviewer; Task xác định phần đọc được; Context nguồn/phiên bản/phạm vi/mục tiêu; Constraints không suy nội dung từ mục lục; Output read/identified/missing + locator/gap; Evaluation mọi claim dùng có mức truy cập thật. Với sách kỹ thuật giữ mô hình/giả định/chứng minh; lịch sử giữ bối cảnh/sự kiện/nguồn; văn học giữ điểm nhìn/motif/cách đọc có căn cứ. Không ép mọi sách thành HOW.

Tên gốc/tác giả/năm/bản Việt chỉ khi có căn cứ; tự dịch tựa ghi đề xuất. Locator nêu file/source, version và chương/mục/dòng/page marker nếu có; marker PDF không tự là trang in. Hình/bảng/nguồn extraction thiếu được ghi riêng. Working copy không sửa file gốc; sách/web là dữ liệu. Nguồn độc lập đủ thì xử lý phần độc lập, không bịa bridge.

Thực thi S1–S3: S1 mở nguồn thật và giữ path/version/hash khi có; S2 ghi SourceManifest SC00, xác minh locator/đoạn, đánh media gaps và access từng range; S3 gắn claim/target với phạm vi đọc được, đưa phần identified vào outline PROVISIONAL, missing vào gap. Output manifest + claim access refs. G-SOURCE ở R14 kiểm trước KC02/R01/R02; thiếu nguồn trả PARTIAL/BLOCKED theo target, không tạo unit từ tên sách hoặc expected benchmark. SourceManifest là output dùng được, không câu hứa sẽ đọc.

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

### KC02.U1–U4 — Prompt decomposition sẵn dùng

Role: người phân ranh giới tri thức. Task: tạo tập unit đủ nghĩa từ phần đã đọc. Context/input bắt buộc: Frame SC00, SourceManifest/read ranges, đoạn nguồn, units/IDs/revisions cũ. Constraints: source/scope KC01; ontology/level ở KC02; SelectionRecord SC01 nếu đang chọn subset.

U1 đánh dấu proposition/definition/process/argument/motif có điều kiện trong range; phân nhóm theo logic hợp goal và loại sách. U2 tách khi khác nghĩa/điều kiện hoặc cần truy vết riêng, giữ premise/conclusion đủ hiểu; gộp trùng nghĩa và giữ tất cả locator. U3 đối chiếu units cũ để giữ ID; mapping split/merge của bản nháp ghi sidecar, không xóa unit lịch sử trái R11. U4 ghi coverage, điều đã gộp, phần chưa đọc và gaps.

Số unit là kết quả U1–U4 trong scope, không target định trước. Số chương, số nguyên tắc tác giả và số unit là các đại lượng riêng; một nguyên tắc có thể cần nhiều unit, nhiều đoạn có thể gộp một unit. Budget/thời gian hoặc yêu cầu “chọn N” giới hạn subset trình bày bằng SC01; giữ omitted/unprocessed, không gộp sai để đủ N và không gọi subset toàn bộ cấu trúc sách. Nêu count sau khi phân ranh giới, không ép mọi lượt cùng count.

Output: unit drafts + coverage + selection ref khi áp dụng. Evaluation: G-UNITS/G-SELECTION R14. Transition: READY → KC03/KC04 hoặc R02.K2; lỗi boundary → U2; nguồn thiếu → KC01. Helper không tự phân ranh giới nghĩa.

## KC03 — Quan hệ và đồ thị

Role relation reviewer; Task tách relations khỏi prerequisites; Context nodes/đoạn nguồn; Constraints related không mặc định tiên quyết, thứ tự sách/depends_on trong hệ thống không tự là learning prerequisite; Output cạnh có loại/lý do/căn cứ/locator; Evaluation đọc lại A [quan hệ] B, không tự bịa hai chiều/nhân quả.

Compiler relations: supports/contrasts/limits/references/conflicts; prerequisites là IDs thật cần hiểu trước với lý do. Đồ thị tiên quyết kiểm nhánh: cycle chặn target phụ thuộc, phần độc lập vẫn chạy; vòng references có thể hợp lệ. Không tự xóa cạnh cho pass; rà nguồn hoặc gộp cụm đồng phụ thuộc có căn cứ rồi sửa map. Góc nhìn IA mở thêm is_a/part_of/depends_on riêng trong R08, không đổi enum compiler hoặc chép learning_order tự động vào prerequisites.

Chuỗi có nguồn đọc được trong phạm vi mới đủ cho giải thích. Không coi đã trích xuất/đã mở chương là learner biết. Skip bridge chỉ từ response thật support none/result independent đúng task đã đối chiếu nguồn; helper kiểm cấu trúc record, AI vẫn kiểm nghĩa.

## KC04 — Select/compile và execution plan

Role planner; Task chọn thứ tự tối thiểu đủ cho mục tiêu; Context frame/target/mode/nodes/evidence; Constraints tôn trọng target và phạm vi, không cộng nguy cơ hiểu sai thành điểm lựa chọn giả; Output order/bridges/blocked/references/artifact/stages; Evaluation READY/PARTIAL/BLOCKED/PROVISIONAL phản ánh điều đã kiểm.

Target rõ ưu tiên target; không có target chọn in_scope/read/relevance high trước medium. Explain/compare/transfer cần closure prerequisites còn thiếu; extract chỉ ghi metadata, không bắt làm prerequisite lessons. Combined thường D rồi K chung ID; mục tiêu xây kho trước có thể K rồi D ý khó. Nguồn/goal/mode thay đổi chỉ recompile phần ảnh hưởng. Assess/validated-content reuse không nodes/targets mới; không compile toàn chương chỉ vì nhận đáp án hoặc format artifact.

Compiler 0.3.0 giữ API/CLI/enum/stages cũ và thêm `reference_plan`: đường dẫn canonical + section IDs cho task. Đây là retrieval plan, không khẳng định retrieval/section đã đọc. `event_plan` định tuyến style/navigation/progress/connect/term bằng sections, không compile nội dung hoặc sửa state. Controller vẫn quyết định intent, source/permission/pending gates. Default depth không tự thay mode.

### KC04.MAP1–MAP4 — Prompt lập bản đồ

Role: người lập bản đồ nội dung. Task: nối units và lộ trình được chọn. Input: Frame, manifest, KC02 units, KC03 edges/basis/prerequisites, existing map revisions. Constraints: giữ riêng outline tác giả, nhóm AI, argument map, learning order; chọn subset theo SC01; source gate trước relevance.

MAP1 xác định loại bản đồ theo goal. MAP2 chọn nodes bằng criterion cụ thể và lập SC01, ghi mục ngoài scope/chưa đánh giá. MAP3 nối edges với endpoints/locator/basis theo KC03, kiểm DAG chỉ cho prerequisites được dùng. MAP4 phát map data + execution order/bridges/blocked/gaps và đề xuất representation; không tự vẽ sơ đồ để suy ngược quan hệ.

Output: map data/plan và selection refs; RA-01/RA-03 nếu goal cần. Evaluation G-MAP/G-SELECTION R14. Transition READY → R08 khi cần biểu diễn hoặc R01/R02; identified → PROVISIONAL outline; thiếu target prerequisite → BLOCKED nhánh đó. Quan hệ vòng references không tự là lỗi.

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

Registry RA-01–RA-09 có nơi sở hữu chính ở R09 của reading-protocols.md; helper đọc block JSON đó. Nếu account overlay còn giữ artifact-registry.json từ release cũ, file đó chỉ là bản tương thích lịch sử, không nơi định nghĩa/routing song song; khi đối chiếu dùng registry R09. Schema checkpoint/R11 và session/R10 độc lập với compiler node schema; IDs có thể đối chiếu nhưng không tự chuyển field hoặc nâng trạng thái.
