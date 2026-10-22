# Changelog / Nhật ký thay đổi

These notes summarize user-facing and compatibility changes. / Ghi chú này tóm tắt thay đổi đối với người dùng và khả năng tương thích.

## 0.3.5 — 2026-10-23

- **Continuity (issue #8):** session support can no longer be laundered from `unknown` to `none` through an intermediate save; legacy questions without a context cannot be assigned a known support or resolved as `independent`; a resolving assessment cannot record less support than the question actually had. The `test_rs_a01` expectation that treated `unknown → none` as allowed was superseded against SC04/R11 — see the supersession note in the test. Behavior change from this release onward; transitions are guarded, past states are not rewritten retroactively. / **Continuity (issue #8):** support của phiên không còn bị “rửa” từ `unknown` thành `none` qua một lần save trung gian; câu hỏi legacy không có context không thể bị gắn support đã biết hoặc được resolve thành `independent`; assessment khi resolve không được ghi support thấp hơn support thật của câu hỏi. Kỳ vọng cũ của `test_rs_a01` cho phép `unknown → none` đã bị supersede theo SC04/R11 — xem ghi chú supersession trong test. Đây là thay đổi hành vi từ bản này; guard chỉ chặn chuyển đổi mới, không hồi tố state cũ.
- GitHub release line 0.3.5 — supersedes the unreleased fixes accumulated since 0.3.3 (PR #6, PR #7, PR #9); the private 0.3.4 candidate is a separate line and is not part of this release. / Tuyến phát hành GitHub 0.3.5 — gộp các sửa chữa chưa phát hành kể từ 0.3.3 (PR #6, PR #7, PR #9); candidate riêng 0.3.4 là tuyến tách biệt, không thuộc bản phát hành này.

### Routing fix / Sửa định tuyến

- **KC-08:** the `transfer` reference plan now includes `R13` — `reference_plan('transfer')` returns `[R09, R13, R04, R06]` — so the examples & transfer owner section is retrieved directly instead of only via R09's prose pointer, closing the known routing gap. Decision by NohFinl, 2026-10-23. / **KC-08:** kế hoạch truy hồi của `transfer` nay có `R13` — `reference_plan('transfer')` trả `[R09, R13, R04, R06]` — nên section chủ sở hữu ví dụ và transfer được truy hồi trực tiếp thay vì chỉ qua con trỏ văn xuôi của R09, đóng khoảng trống định tuyến đã biết. Quyết định của NohFinl, 2026-10-23.

### Documentation update / Cập nhật tài liệu

- Added paired Vietnamese/English architecture, principle and quality guides; clarified document navigation and canonical owners. / Bổ sung cặp tài liệu kiến trúc, nguyên lý và chất lượng VI/EN; làm rõ điều hướng và file canonical.

### Security hardening / Gia cố an ninh

- Helpers hardened after an independent red-team / pen-test wave: checkpoint field-set locking, duplicate-JSON-key rejection, clean `{ok: false}` on deeply nested JSON in all CLIs, input size caps, streaming source reads with a 1 MiB per-line cap, consistent output symlink checks, minimum grounding-excerpt size, `source_root` scoping for sources, and fixed `timestamp()` timezone diagnostics plus a reachable `Cannot overwrite source` export guard. Full suite: 542 passed; 39/39 red-team probes blocked in independent acceptance. / Các helper được gia cố sau vòng red team / pen test độc lập: khóa tập trường của checkpoint, chặn duplicate JSON key, trả `{ok: false}` sạch khi JSON lồng sâu ở mọi CLI, giới hạn kích thước input, đọc nguồn theo luồng với cap 1 MiB/dòng, kiểm symlink ở output nhất quán, ngưỡng tối thiểu cho excerpt căn cứ, gắn `source_root` cho nguồn, và sửa chẩn đoán timezone của `timestamp()` cùng guard `Cannot overwrite source` trong export. Toàn bộ suite: 542 passed; nghiệm thu độc lập chặn 39/39 probe red team.
- **Sibling guard instances (issue #5, PR #6, merged 2026-10-23):** the `checked_at` timezone diagnostic for `current_source` units in `checkpoint.validate()` now surfaces its specific message instead of the generic timestamp error, and the differ-from-source guard in `checkpoint.initialize()` runs before the already-exists guard so its diagnostic is reachable. Full suite after this PR: 544 passed. / **Hai instance anh em của guard (issue #5, PR #6, merge 2026-10-23):** chẩn đoán timezone của `checked_at` cho unit `current_source` trong `checkpoint.validate()` nay hiện đúng thông điệp chuyên biệt thay vì lỗi timestamp chung, và guard differ-from-source trong `checkpoint.initialize()` chạy trước guard already-exists để thông điệp của nó chạm tới được. Toàn bộ suite sau PR này: 544 passed.

## 0.3.3

### Tiếng Việt

- Làm rõ ba mode đọc `deep`, `extract`, `combined` và cách giữ liên kết nguồn cùng trạng thái học.
- Cải thiện hướng dẫn trích xuất tri thức, nối ví dụ với khái niệm, checkpoint và bàn giao phiên.
- Bổ sung kiểm tra repository và helper cho maintainer.

### English

- Clarified the `deep`, `extract` and `combined` reading modes and how source links and learning state are preserved.
- Improved guidance for knowledge extraction, example-to-concept links, checkpoints and session handoff.
- Added repository and helper checks for maintainers.
