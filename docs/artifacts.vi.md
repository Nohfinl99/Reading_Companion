# Danh mục đầu ra Reading Companion

[English](artifacts.en.md) · [Ví dụ tổng hợp](examples/outputs.md) · [Bản đồ tài liệu](README.md)

Đây là chỉ mục đủ chín ID RA-01–RA-09 trong [registry canonical R09](../skills/sid-reading-companion/references/reading-protocols.md#r09--output-artifacts-oa1oa4). Các ví dụ mới do AI soạn để minh họa tài liệu; chúng chưa được chạy/chấm như phiên học. Đủ mục trong danh mục không có nghĩa chín năng lực đã được kiểm đạt. R09 sở hữu required fields; trang này không tạo schema thứ hai.

## Chọn đầu ra theo công việc

| ID / đầu ra | Mục tiêu và đầu vào cần có | Kết quả người đọc nhận | Owner nội dung / contract |
|---|---|---|---|
| RA-01 — Knowledge Map | Xem cấu trúc phần đã đọc; cần scope, source access, nodes/relations và locators | Outline, bảng hoặc sơ đồ có phạm vi, nguồn từng node và gaps | KC03/KC04, R08; R09 |
| RA-02 — Concept Card | Làm rõ một khái niệm; cần đoạn nguồn và điều kiện | Định nghĩa, điều kiện/giới hạn, locator; không mặc định phải biến mọi giải thích thành thẻ | R01/R02; R09 |
| RA-03 — Argument Map | Hiểu vì sao kết luận được rút ra; cần premises, evidence, conditions | Mạch premises → conclusion có locators và căn cứ của từng quan hệ | R01/R08; SC02, R09 |
| RA-04 — Comparison Matrix | So các lựa chọn theo cùng câu hỏi; cần options, criteria và bối cảnh tương thích | Bảng tiêu chí chung, compatible contexts, locators và kết luận giới hạn | R03; R09 |
| RA-05 — Knowledge Library | Lưu tri thức đủ nghĩa; cần units đã phân ranh giới và nguồn | IDs, content, conditions, knowledge levels, citations, relations; giữ gap metadata | KC02/KC03, R02; R09/R11 |
| RA-06 — Recall Card | Nhắc lại một unit đã kiểm; cần checked unit và critical conditions | Thẻ ngắn bổ sung có locator, giữ điều kiện; không thay unit đầy đủ | R02; R09 |
| RA-07 — Transfer Exercise | Thử áp dụng vào tình huống mới khi được yêu cầu; cần target, source limits và dữ kiện đủ | Outcome, new situation, source limits và một câu hỏi không đáp án | R13/R04; SC03/SC04, R09 |
| RA-08 — Learning Checkpoint | Phản hồi sau response thật; cần question, raw response/skip, support và criterion gốc | Feedback ngắn và observed result có giới hạn; skip không thành assessment | R04/R05; SC04, R09/R11 |
| RA-09 — Session Handoff | Nối phiên/bàn giao; cần goal, mode, scope, source access, processed IDs, pending và limitations có thật | Bản bàn giao có nguồn/state/Q/support/gaps; file đã lưu được liệt kê riêng | R12/R10/R11; SC00, R09 |

`deep/extract/combined` và style vẫn do phiên quyết định. Extract không quiz. RA-07 chỉ phát thành câu hỏi khi có yêu cầu tương ứng và criterion đã chuẩn bị; không tự chen vào lượt extract. Một pending Q không được giải phóng bởi việc tạo map/card/handoff.

## Ví dụ và mức bằng chứng hiện có

| Output | Ví dụ tài liệu | Artifact/bằng chứng đã lưu khác | Khoảng trống còn lại |
|---|---|---|---|
| RA-01 | [Map mẫu](examples/outputs.md#ra-01) | [Helper map tests](../tests/test_ia_map.py), [compiler tests](../tests/test_knowledge_compiler.py) | Ví dụ chưa có semantic review hoặc host capture riêng |
| RA-02 | [Concept card mẫu](examples/outputs.md#ra-02) | [Knowledge CiteGuard](../skills/sid-reading-companion/references/knowledge/citeguard.md) là tri thức có nguồn liên quan, không tự chứng minh card output đã đạt | Chưa có run/review riêng cho card này |
| RA-03 | [Argument map mẫu](examples/outputs.md#ra-03) | SC02 định nghĩa contract; CE captures có diễn giải nhưng không tự là bộ ArgumentRecord hoàn chỉnh | Chưa có captured SC02/RA-03 run riêng |
| RA-04 | [Comparison mẫu](examples/outputs.md#ra-04) | [Artifact CE được Luna sinh](../evaluation/citeguard/sync-0.3.7/artifact.md) diễn giải 60/40 có nguồn; không phải run kiểm mọi comparison matrix | Chưa có matrix run/review riêng |
| RA-05 | [Library mẫu](examples/outputs.md#ra-05) | [Knowledge/package manifest](../skills/sid-reading-companion/references/knowledge/citeguard-source.json); [unit fixtures](../tests/conftest.py) phục vụ helper tests | Mẫu library chưa qua model/host evaluation riêng |
| RA-06 | [Recall card mẫu](examples/outputs.md#ra-06) | R02/R09 định nghĩa mục đích và dữ liệu bắt buộc | Chưa có recall-card run hoặc dữ liệu nhớ lâu |
| RA-07 | [Learner prompt mẫu](examples/outputs.md#ra-07) | SC03/SC04 có contract cho example/criterion; mẫu chưa là câu hỏi đã phát trong phiên | Chưa có actual learner transfer response; không chứng nhận G-Q từ template |
| RA-08 | [Feedback demo tổng hợp](examples/outputs.md#ra-08) | [Checkpoint tests](../tests/test_checkpoint.py) dùng synthetic state; không xác minh nguồn gốc response thật | Chưa có learner outcome; không ghi demo vào learner history |
| RA-09 | [Layout bàn giao mẫu](examples/outputs.md#ra-09) | [Bundle spec](../specs/handoff-bundle-v1.md), [helper roundtrip tests](../tests/test_handoff_bundle.py) | Chưa có installed-host/new-chat handoff capture; layout không phải bundle đã lưu |

Các helper tests kiểm cấu trúc, state và transitions trong fixture được tạo khi test chạy. Các ví dụ trong trang này thuộc lớp **authored documentation example**, không phải observed model output. Bằng chứng model-run thực cho CE gồm [artifact](../evaluation/citeguard/sync-0.3.7/artifact.md), [SC05 sidecar](../evaluation/citeguard/sync-0.3.7/sidecar.json), [manifest](../evaluation/citeguard/sync-0.3.7/run-manifest.json) và [primary review](../evaluation/citeguard/sync-0.3.7/review.json): một case tổng hợp, ba tiêu chí, có attempt1 và một lần sửa được giữ. Nó không tạo kết quả “9/9”. Host activation, persistence trên chat mới và learner outcomes vẫn cần capture riêng.

## Records và file bàn giao

[SC00–SC05](../skills/sid-reading-companion/references/stack-contracts.md) định nghĩa dữ liệu dùng chung:

| Contract | Trách nhiệm | Mức hiện có / cách dùng |
|---|---|---|
| SC00 — Envelope | Source/hash/version, state revision, unit revisions, artifact refs và gaps | Contract canonical; [bundle spec](../specs/handoff-bundle-v1.md) kiểm identity/dependencies theo manifest riêng, không thay toàn bộ kiểm nghĩa |
| SC01 — SelectionRecord | Ai chọn, scope/universe, criterion, members, count basis và phần chưa xét | Contract; [lời dẫn chọn mẫu](examples/outputs.md#selection) là minh họa, chưa là selection history đã quan sát |
| SC02 — ArgumentRecord | Premises, typed links, conclusion, conditions, exceptions, source locators | Contract và [argument mẫu](examples/outputs.md#ra-03); chưa có run record riêng được certify |
| SC03 — ExampleLink | Nối scenario với units/argument và giới hạn suy ra | Contract; [transfer mẫu](examples/outputs.md#ra-07) chỉ là learner view, không giả full sidecar đã tồn tại |
| SC04 — QuestionContract | Criterion chuẩn bị trước Q, target/revision, support context và validity | Criterion/answer ở evaluator sidecar; không kèm learner prompt/handoff khi Q pending |
| SC05 — GateRecord | Artifact/revision, applicability, status, evidence spans, checks, owner và unresolved | [Actual sidecar mới](../evaluation/citeguard/sync-0.3.7/sidecar.json) được strict validator kiểm; semantic review vẫn riêng |

Checkpoint JSON thuộc R11 và bốn helper hiện có; không nhét SC records vào `pending_question`, unit hoặc session nếu schema chưa hỗ trợ. `checkpoint.py export` không tự xuất mọi sidecar. Handoff cần gửi state, nguồn và sidecar thực có, kiểm hash/revision; thiếu file thì nói rõ chưa lưu. [Bundle utility](../tools/validate_handoff_bundle.py) là development checker, không tự restore/migrate hoặc tạo bộ nhớ tài khoản.

## Phân biệt những thứ có thể tải

- **Reading output/handoff:** tri thức và trạng thái của một phiên đọc, có quyền truy cập nguồn và evaluator separation riêng.
- **Research/evaluation evidence:** Knowledge có attribution, synthetic fixtures, raw/model outputs và review. Paper metrics không phải accuracy của SID; hồ sơ kiểm không phải learner history.
- **Plugin release package:** ZIP runtime và release manifest từ [allowlist](../packaging/runtime-files.json)/[builder](../tools/build_plugin.py), dùng để phân phối plugin. Nó không phải checkpoint/handoff và không mang theo phiên học cá nhân.

Xem [artifact index ở root](../ARTIFACTS.md) để tìm source, evidence và quy tắc tải package. Không suy một file đã được upload/download hoặc một release đã được host nạp chỉ vì có mô tả tại đây.
