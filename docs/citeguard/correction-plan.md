# Đồng bộ Reading Companion 0.3.7

Baseline audit: source `709d19bc27c65270a487a5aa0a6eb6fde67d74f7`, account plugin 0.3.6. Bản 0.3.7 triển khai sửa source/package parity và contract gate; hồ sơ này phân biệt kiểm cơ học, delegated model và host.

## Thay đổi

1. Hợp nhất guard giữ assessment/Q/support vào source; thêm ca sai và ca hợp lệ, giữ checkpoint schema/CLI.
2. Nối validator SC05 dùng chung với authored adapter và sidecar mới. Historical integrity vẫn kiểm được bằng source snapshot; lỗi SC05 của CE-T01 cũ giữ riêng, không sửa raw hoặc frozen rubric.
3. Thêm allowlist/build/verify package xác định; source là đầu vào duy nhất. Metadata/audience/identity của plugin được giữ, version tăng lên 0.3.7.
4. Thêm checker bundle development-only: kiểm state/sidecar/dependencies/stale/rebind; không tự sửa state, hiểu nguồn hay chấm người học.
5. Cập nhật README song ngữ, usage, mapping CE capability và application notes có nhãn SID.

## Ownership và nghiệm thu

M/KC/R/SC tiếp tục giữ owner hiện có. CE06 thuộc G-CITATION-REVIEW/R14; handoff theo R12/G-HANDOFF. Không thêm gate runtime cạnh tranh. Source release cần regression liên quan, schema/evidence validation, deterministic package và parity. Host readiness cần chạy trên đúng release thật sau activation.

## Bằng chứng

Candidate local regression: **PASS — 662 tests trên Linux/Python 3.12.15** ở lượt kiểm full suite trước khi thêm validator provenance cho capture mới. Packaging verifier bổ sung ca manifest default/one-skill; các ca mới được kiểm riêng và CI chạy lại toàn bộ trên Python 3.10–3.12. Xem [workflow theo nhánh/commit](https://github.com/Nohfinl99/Reading_Companion/actions/workflows/validate.yml) và [release checks](https://github.com/Nohfinl99/Reading_Companion/blob/feat/sid-v5-citeguard-reading/evaluation/citeguard/sync-0.3.7/release-checks.json) để xác định đúng candidate cuối, không dùng số lịch sử cho run mới.

Một lượt gpt-6-luna mới sinh artifact + SC05 JSON sidecar từ context snapshot. Primary yêu cầu sửa applicability của CR05 cho extract/no-quiz; attempt1 giữ nguyên. Bản cuối đạt ba tiêu chí đã đóng băng và validator strict với caller revision baseline. Đây là một case tổng hợp, không phải độ chính xác tổng quát. [Capture và review](https://github.com/Nohfinl99/Reading_Companion/tree/feat/sid-v5-citeguard-reading/evaluation/citeguard/sync-0.3.7).

Historical Luna: ba lượt/30 raw outputs được giữ; lượt 3 đạt frozen behavioral rubric nhưng CE-T01 thiếu SC05 fields. Sidecar mới bắt buộc đầy đủ schema; reviewer vẫn kiểm nghĩa riêng.

Installed-host activation/new-chat persistence, quality/cost gain và learner outcomes: **NOT_RUN** cho tới khi có capture riêng. Bộ kiểm bundle chỉ chứng minh cấu trúc/identity trong scope đã chạy. Khi không có file/Python, dùng handoff trong chat và ghi chưa lưu/kiểm tool.

## Dùng bản mới

Xem [hướng dẫn tiếng Việt](../usage.vi.md) hoặc [English guide](../usage.en.md). Gửi nguồn thực, goal/scope/mode. Khi yêu cầu review citation, giữ artifact và SC05 JSON sidecar; khi chuyển chat, gửi nguồn/checkpoint/sidecars và giữ criterion evaluator ngoài learner view. Repository tools không tự cài thêm tool lên host.

## Các bước còn lại

Kiểm chuỗi deep/combined → Q → hint → CE → pause/navigation → handoff → phiên mới/resume → source revision đổi trên host thực. Chỉ báo readiness của lớp có bằng chứng. Không đổi source hoặc xóa Q để đạt gate. Chưa phát triển corpus-search/MCP, account memory hoặc adapter PDF tổng quát.
