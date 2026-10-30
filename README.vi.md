# Reading Companion

<img src="assets/logo.svg" alt="Reading Companion" width="96" />

![Plugin version](https://img.shields.io/badge/Plugin-0.3.8-15324F)
[English](README.md) · [Hướng dẫn sử dụng](docs/usage.vi.md) · [Thay đổi](CHANGELOG.md)

Reading Companion hỗ trợ đọc sâu, trích xuất tri thức có nguồn và giữ checkpoint đọc bằng tiếng Việt. Tên kỹ thuật: `sid-reading-companion`. Gói gồm một skill và năm helper Python tùy chọn.

Bản 0.3.8 bổ sung route tường minh cho audit bằng chứng dự án và helper packaged kiểm đủ structured record, render các trường bắt buộc. Semantic review vẫn độc lập. Xem [hướng dẫn bằng chứng dự án](docs/project-evidence.vi.md) và [giới hạn bằng chứng release](docs/citeguard/correction-plan.md).

## Bắt đầu đọc

Đính kèm nguồn thực rồi nêu mục tiêu, phạm vi và mode:

> Em đọc mục 2 ở mode combined, style standard. Mục tiêu: hiểu vì sao tác giả kết luận X và lưu kiến thức dùng cho Y. Giải thích mạch lập luận, giữ điều kiện/ngoại lệ, bổ sung unit có locator. Cuối cụm hỏi một câu rồi chờ anh trả lời.

| Mode | Cách làm |
|---|---|
| `deep` | Giải thích nghĩa và lập luận; style standard hỏi một câu rồi chờ. |
| `extract` | Tạo unit có nguồn, điều kiện và quan hệ; không quiz. |
| `combined` | Phần giải thích và trích xuất dùng chung ID; giữ câu hỏi đang chờ. |

Style chỉ đổi cách trình bày. Gợi ý đã nhận vẫn phải được ghi nhận là hỗ trợ. Mở chương hoặc tạo thẻ không chứng minh đã hiểu.

## Kiểm claim với nguồn

> Em đối chiếu claim [C] với tài liệu anh đính kèm trong [phạm vi]. Chỉ rõ nguồn/vị trí, mức hỗ trợ, điều kiện quyết định và phần chưa rõ. Áp dụng vào artifact đọc rồi rà bản cuối, giữ mode và không giải đáp câu hỏi đang chờ.

Tách tìm citation phù hợp, kiểm nguồn có hỗ trợ claim và xác minh sự thật bên ngoài. Knowledge CiteGuard cùng CE01–CE06 hướng dẫn host làm việc; không tự cài corpus search hoặc dịch vụ kiểm citation.

## Nối phiên ở chat mới

Yêu cầu handoff giữ nguồn/version/hash, unit ID/revision, vị trí, Q pending/paused, lịch sử hỗ trợ và gaps. Gửi lại nguồn, checkpoint và sidecar đã sinh cho chat mới. Tiêu chí/đáp án evaluator nằm ngoài bản người học nhìn thấy khi Q còn pending.

Plugin không có memory tài khoản. `checkpoint.py export` không tự xuất mọi sidecar. Checker bundle trong repository giúp phát hiện file thiếu/stale; host phải thực sự chạy trước khi báo kiểm cấu trúc đã đạt.

## Cấu trúc và nguồn chuẩn

`SKILL → M04 → nguồn/units → protocol đọc hoặc citation → R14/SC05 → R12 handoff`

- Controller M01–M07 sở hữu routing và scope.
- Knowledge Compiler sở hữu nguồn, ranh giới/số unit và quan hệ.
- Reading protocols sở hữu giải thích, Q/support, state và handoff.
- SC00–SC05 định nghĩa artifact trao đổi; CE06 dùng G-CITATION-REVIEW hiện có.
- Bốn helper kiểm plan/map/checkpoint/state. Kiểm nghĩa và claim support vẫn cần reviewer đối chiếu nguồn.

## Kiểm chứng và đóng gói

Trong repository, dùng Python 3.10–3.12:

```sh
python tools/validate_repository.py
python tools/validate_citation_evidence.py
python tools/validate_luna_rerun.py
python -m pytest -q
python tools/build_plugin.py --root . --output ../reading-companion.zip --source-commit <commit-sha>
```

Allowlist runtime nằm ở `packaging/runtime-files.json`. Build từ commit đã pin, kiểm staged package và so readback sau update. File legacy còn trên backend được phân biệt với canonical runtime.

Lịch sử Luna giữ nguyên raw output và rubric, gồm lỗi SC05 thiếu trường ở CE-T01. PASS hành vi cũ không chứng minh schema đạt. Record mới phải qua validator strict và kiểm nghĩa riêng. Helper không chứng minh host đã nạp, citation accuracy tổng quát, giảm chi phí hay hiệu quả học. [Hồ sơ sửa](docs/citeguard/correction-plan.md) nêu bằng chứng thực và phần chưa chạy.

Công cụ chỉ có trong repository: [tools/tests](https://github.com/Nohfinl99/Reading_Companion/tree/feat/sid-v5-citeguard-reading) · [hồ sơ run lịch sử](https://github.com/Nohfinl99/Reading_Companion/tree/709d19bc27c65270a487a5aa0a6eb6fde67d74f7/evaluation/citeguard).

## Giấy phép

[MIT](LICENSE). Giữ nguồn gốc của claim nghiên cứu. Gói runtime không phân phối sách riêng hoặc tài liệu khóa học SID gốc.
