# Changelog / Nhật ký thay đổi

These notes summarize user-facing and compatibility changes. / Ghi chú này tóm tắt thay đổi đối với người dùng và khả năng tương thích.

## Routing fix / Sửa định tuyến — unreleased

- **KC-08:** the `transfer` reference plan now includes `R13` — `reference_plan('transfer')` returns `[R09, R13, R04, R06]` — so the examples & transfer owner section is retrieved directly instead of only via R09's prose pointer, closing the known routing gap. Decision by NohFinl, 2026-10-23. / **KC-08:** kế hoạch truy hồi của `transfer` nay có `R13` — `reference_plan('transfer')` trả `[R09, R13, R04, R06]` — nên section chủ sở hữu ví dụ và transfer được truy hồi trực tiếp thay vì chỉ qua con trỏ văn xuôi của R09, đóng khoảng trống định tuyến đã biết. Quyết định của NohFinl, 2026-10-23.

## Documentation update / Cập nhật tài liệu — unreleased

- Added paired Vietnamese/English architecture, principle and quality guides; clarified document navigation and canonical owners. / Bổ sung cặp tài liệu kiến trúc, nguyên lý và chất lượng VI/EN; làm rõ điều hướng và file canonical.

## Security hardening / Gia cố an ninh — unreleased

- Helpers hardened after an independent red-team / pen-test wave: checkpoint field-set locking, duplicate-JSON-key rejection, clean `{ok: false}` on deeply nested JSON in all CLIs, input size caps, streaming source reads with a 1 MiB per-line cap, consistent output symlink checks, minimum grounding-excerpt size, `source_root` scoping for sources, and fixed `timestamp()` timezone diagnostics plus a reachable `Cannot overwrite source` export guard. Full suite: 542 passed; 39/39 red-team probes blocked in independent acceptance. / Các helper được gia cố sau vòng red team / pen test độc lập: khóa tập trường của checkpoint, chặn duplicate JSON key, trả `{ok: false}` sạch khi JSON lồng sâu ở mọi CLI, giới hạn kích thước input, đọc nguồn theo luồng với cap 1 MiB/dòng, kiểm symlink ở output nhất quán, ngưỡng tối thiểu cho excerpt căn cứ, gắn `source_root` cho nguồn, và sửa chẩn đoán timezone của `timestamp()` cùng guard `Cannot overwrite source` trong export. Toàn bộ suite: 542 passed; nghiệm thu độc lập chặn 39/39 probe red team.

## 0.3.3

### Tiếng Việt

- Làm rõ ba mode đọc `deep`, `extract`, `combined` và cách giữ liên kết nguồn cùng trạng thái học.
- Cải thiện hướng dẫn trích xuất tri thức, nối ví dụ với khái niệm, checkpoint và bàn giao phiên.
- Bổ sung kiểm tra repository và helper cho maintainer.

### English

- Clarified the `deep`, `extract` and `combined` reading modes and how source links and learning state are preserved.
- Improved guidance for knowledge extraction, example-to-concept links, checkpoints and session handoff.
- Added repository and helper checks for maintainers.
