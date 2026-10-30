# Hướng dẫn bằng chứng nguồn dự án

**Dùng khi người dùng yêu cầu tra cứu, đối chiếu hoặc bàn giao bằng chứng cho một dự án.** Đây không phải checkpoint hay bộ máy truy xuất mới. Một profile audit additive ngoài learner state schema được mô tả tại [runtime reference](../skills/sid-reading-companion/references/project-evidence.md) và [SC00–SC01 owner](../skills/sid-reading-companion/references/stack-contracts.md); helper packaged kiểm cấu trúc/freshness và render phần bắt buộc hiển thị, không kiểm semantic truth. Hãy dùng đúng source root, component, revision và quyền truy cập đã được giao. Nếu thiếu căn cứ về authority hoặc revision, giữ kết luận unresolved và chỉ dùng phần độc lập có thể xác minh.

## Hợp đồng chuẩn

- [KC01](../skills/sid-reading-companion/references/knowledge-compiler.md) sở hữu source/task frame, truy cập thật, locator và gap.
- [SC00](../skills/sid-reading-companion/references/stack-contracts.md) sở hữu envelope, provenance, persistence boundary và state handoff; [SC01](../skills/sid-reading-companion/references/stack-contracts.md) sở hữu tiêu chí chọn, exclusions và completeness trong verified scope.
- [CE02 và CE04](../skills/sid-reading-companion/references/citation-evidence.md) xử lý source spans và claim support. Citation liên quan chưa chắc hỗ trợ; missing access không chứng minh claim sai. Giữ mâu thuẫn unresolved.
- [R12 và R14](../skills/sid-reading-companion/references/reading-protocols.md) sở hữu continuity handoff và validation. Progress là đọc trạng thái; handoff bằng chứng là thao tác riêng.

## Cách làm

Dùng artifact của phase trước làm context cho phase sau. Mỗi phase chỉ có một cognitive task. Ghi decision facts và locator cần kiểm, không ghi private chain-of-thought. Nếu task chỉ là Progress thì dừng ở state read-only, không gọi compiler hoặc CE. Với yêu cầu kết hợp Progress và handoff, báo state trước rồi xử lý riêng bằng chứng đã có; không suy ra reading state từ bằng chứng ngoài.

### Stack A — Chọn source và xác định authority

| Phase | RTC-COE |
|---|---|
| A1 — Source admission | **Role:** source reviewer. **Task:** xác định đúng source root/component và phần được phép dùng cho objective. **Context:** yêu cầu nguyên văn, source roots hiện có, KC01/SC00 và access thực. **Constraints:** tên file, mtime hay revision mới hơn không tự tạo authority; snapshot hash/ngày xác định byte hoặc thời điểm snapshot đã đọc, không chứng minh implementation revision hay runtime hiện tại; giữ authority basis và scope riêng; không mở rộng quyền truy cập. Nếu implementation revision/runtime không được nguồn xác nhận, ghi unknown/not verified. **Output:** trong phần handoff hiển thị, tách `Source snapshot identity` (path, hash, document date/version quan sát được) khỏi `Implementation revision/current runtime` (giá trị kèm evidence trực tiếp, hoặc unknown/not verified); ghi access/missing ranges. **Evaluation/stop:** G-SOURCE/R14; kiểm người nhận thấy hai mục tách biệt khi claim authority/revision được bàn giao; nếu authority hoặc source thiếu, dừng phụ thuộc đó, giữ unresolved và tiếp phần độc lập. |

### Stack B — Chọn bằng chứng và xử lý correction

| Phase | RTC-COE |
|---|---|
| B1 — Selection | **Role:** evidence selector. **Task:** chọn candidate spans cho một objective đã chốt. **Context:** A1 output, verified source universe, CE02, SC01. **Constraints:** ghi criterion trước khi kết luận; phân biệt relevance và support; nêu included/excluded/not examined; completeness chỉ trong verified scope. **Output:** phần selection trong câu trả lời/handoff phải hiện criterion, included/excluded/not examined, searched boundary và lý do dừng có căn cứ thực (ví dụ: đã có bằng chứng trực tiếp cho objective, chạm budget cap hoặc gặp access gap). Không để boundary/lý do dừng chỉ trong selection record hoặc sidecar. Kèm claim/source locator/basis và selection record khi cần theo SC01. **Evaluation/stop:** kiểm phần người nhận thật sự thấy có cả boundary lẫn lý do dừng; universe/locator thiếu thì PARTIAL hoặc unknown, không tuyên bố toàn corpus. |
| B2 — Correction | **Role:** claim reviewer. **Task:** xác định correction hoặc supersession áp dụng cho claim/scope nào. **Context:** B1, nguồn trước/sau, correction locator và CE04. **Constraints:** ngày mới hơn không tự thay nguồn cũ; chỉ thay claim và scope mà correction nói rõ; không lan trạng thái của một component sang component khác; mâu thuẫn còn lại giữ cả hai. **Output:** claim trước/sau, relation được nguồn xác nhận, locator, điều kiện và gap còn lại. **Evaluation/stop:** nếu thiếu căn cứ về quan hệ hoặc phạm vi, ghi unresolved; không phát biểu toàn hệ thống đã được sửa. |

### Stack C — Phân lớp kết quả và tạo handoff

| Phase | RTC-COE |
|---|---|
| C1 — Evidence layer | **Role:** evidence-layer reviewer. **Task:** gắn từng kết quả vào đúng lớp và scope. **Context:** claim/evidence table, conditions và output dự án. **Constraints:** tách offline, device, product pilot, project/global gate; kết quả một lớp không nâng lớp khác. **Output:** kết luận theo scope, trạng thái đã có, điều kiện/gap và phần NOT_RUN. **Evaluation/stop:** không có evidence đúng lớp thì không kết luận acceptance ở lớp đó. |
| C2 — Handoff | **Role:** continuity editor. **Task:** chuyển tiếp artifact bằng chứng có thể tái kiểm. **Context:** SC00/R12, source/access/hash/revision, claims/locators, gaps và consumer acceptance criteria nếu được cung cấp. **Constraints:** nêu next owner; consumer ACK/acceptance unknown nếu không có record; không giả persisted state, admission, checkpoint hay restored new chat. Source hash/revision đổi thì dừng reuse phụ thuộc và yêu cầu đối chiếu lại; giữ nguyên Q/support trong snapshot đọc được, không xóa hoặc hạ support. Nếu snapshot thiếu, state unknown. **Output:** template bên dưới, gửi kèm refs/sidecar thực nếu có. **Evaluation/stop:** G-HANDOFF/R14; consumer chưa xác nhận thì không ghi accepted/admitted. |

### Stack D — Kiểm coverage và lập backlog

| Phase | RTC-COE |
|---|---|
| D1 — Evidence inventory | **Role:** evidence librarian. **Task:** phân loại evidence thực có theo lớp. **Context:** artifacts/output/revision từ A–C và các records kiểm. **Constraints:** tách design/case, mechanical, model, semantic review, host/device, independent và learner; không tính fixture thành run. **Output:** coverage đã biết/chưa biết, locator và lớp; thiếu record ghi NOT_RUN. **Evaluation/stop:** chỉ phân loại điều có artifact; không suy performance. |
| D2 — Backlog | **Role:** priority planner. **Task:** xếp câu hỏi còn thiếu theo prerequisite và owner. **Context:** D1, impact/scope, nguồn hoặc môi trường cần để đóng gap. **Constraints:** không đặt reliability threshold; không thay test host/learner bằng hướng dẫn hoặc synthetic case. **Output:** backlog gồm gap, evidence cần, prerequisite, owner và lớp dự kiến. **Evaluation/stop:** hoãn item cần môi trường/nguồn chưa có; không tuyên bố hoàn tất. |
| D3 — Coverage review | **Role:** evidence reviewer. **Task:** xác định phạm vi coverage có thể báo cáo. **Context:** backlog, actual records, revision và checks đã chạy. **Constraints:** self-review không độc lập; không gom PASS giữa các lớp; scope fixture không mở rộng thành corpus/project. **Output:** coverage statement, checks/NOT_RUN và unresolved gaps. **Evaluation/stop:** chỉ kết luận cho scope/layer có evidence; phần khác giữ unknown. |

## Template ngắn: claim và handoff

```text
Objective:
Scope: source root | component | authority basis | access
Source snapshot identity: path | SHA-256 | document date/version (observed or unknown)
Implementation revision/current runtime: value + direct evidence locator, or unknown/not verified
Selection: criterion | included refs | excluded/not examined | verified universe | stop reason
Claims:
- Claim and condition:
  Evidence locator/hash:
  Claim support (supported / partial / unsupported / unresolved):
  Epistemic basis (Fact / Interpretation / Assumption / Hypothesis / Recommendation):
  Evidence layer and scope:
  Gap / NOT_RUN:
Correction/supersession: affected claim/scope | basis/locator | unresolved relation
Next owner:
Consumer prerequisites/acceptance criteria:
Consumer ACK: unknown unless an acknowledgement record is present
State/persistence: unknown unless an actual snapshot/record is supplied
```

Đây là audit/handoff, nằm ngoài reading checkpoint. Khi dùng helper, tạo audit record theo profile 0.3.8 rồi render block bắt buộc; không thay block bằng prose riêng. R14 reviewer đánh giá ý nghĩa của stop reason và claim, với record riêng gắn hash chính xác. Không chép evaluator criterion hoặc đáp án vào learner-visible handoff khi pending question còn mở; không thêm field vào checkpoint, reading session, unit hay pending question.

## Backlog bằng chứng và lớp kiểm

Giữ backlog riêng với nội dung đọc: câu hỏi còn thiếu, source/scope cần có, owner, prerequisite và lớp bằng chứng sẽ giải quyết. Theo dõi riêng **design/case specification**, **mechanical validation**, **model output**, **semantic review**, **installed-host/device**, **independent review** và **learner outcome**. Không tính fixture hoặc self-review thành run độc lập; chưa chạy ghi `NOT_RUN`. Không đặt accuracy/reliability từ số lượng case. Chỉ chuyển backlog khi có artifact thực, revision và phạm vi đo phù hợp.

## Công cụ và giới hạn

File browser/terminal và helper `project_evidence.py` có thể kiểm path allowlist của bundle đã export, cấu trúc, locator và SHA-256. Đây là kiểm cơ học, không chứng minh quyền sử dụng, authority, claim support, stop-reason sufficiency, consumer ACK hoặc project acceptance. Helper không sandbox các công cụ hay filesystem khác của agent. Ghi rõ phần chưa truy cập/chưa kiểm và không nâng status từ mechanical PASS.
