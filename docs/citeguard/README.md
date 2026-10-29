# CiteGuard integration / Tích hợp CiteGuard

Vietnamese-first project pack based on SID V5. This is a scoped source candidate, not a claim of installed-host validation or learning gain.

Gói này đưa kiến thức có nguồn vào tác vụ đọc qua sáu phase RTC-COE, rồi kiểm lại artifact sau áp dụng. Runtime được định nghĩa trong [CE01–CE06](../../skills/sid-reading-companion/references/citation-evidence.md); tài liệu ở đây giải thích dự án, không tạo instruction song song.

## Đi theo mục tiêu / Choose a route

| Tôi muốn / Goal | Đọc / Read |
|---|---|
| Hiểu bài toán, phạm vi, người dùng | [Framing brief và scope](framing.md) |
| Xem cách phân IA và tìm đúng tài liệu | [IA pack](information-architecture.md) |
| Copy prompt từng phase và gate sau áp dụng | [Prompt Stack RTC-COE](../../skills/sid-reading-companion/references/citation-evidence.md) |
| Kiểm nguồn phương pháp thiết kế SID V5 | [Mapping và provenance](sid-v5-mapping.md) |
| Đọc Knowledge Package | [Tri thức CiteGuard](../../skills/sid-reading-companion/references/knowledge/citeguard.md) |
| Xem ví dụ áp dụng vào reading và tự kiểm | [Walkthrough và bằng chứng](../../evaluation/citeguard/README.md) |
| Xem prototype, sửa lỗi và release checklist | [Revision notes](revision-notes.md) |
| Xem roadmap và lượt chạy Luna có reviewer riêng | [Roadmap chạy lại](roadmap.md), [kết quả lượt cuối](../../evaluation/citeguard/luna-rerun-2026-10-29-r3/README.md) |

## Quick start

```text
Mode extract. Đối chiếu claim bên dưới với phần tài liệu tôi cung cấp.
Áp dụng CE01–CE06, giữ ngữ cảnh và điều kiện; kết thúc bằng GateRecord
G-CITATION-REVIEW cho artifact. Không đánh đồng nguồn liên quan với hỗ trợ.
Claim: [mệnh đề cần kiểm]
Nguồn/phạm vi: [file hoặc đoạn được phép đọc]
```

The stack uses tools already available on the host. It adds no search service, account memory, external API connection, or automatic checkpoint migration. `G-CITATION-REVIEW` is a specialized R14 gate using SC05. The public examples are synthetic fixtures and assistant-authored self-review, not captured user learning records.

## Publication boundary

Public source includes paraphrased knowledge, design, synthetic fixtures, validators and test evidence. Private course files, the pasted proposal, PDF binaries, credentials and personal reading sessions are excluded. Preserve the existing MIT license for this project's code; external research remains credited to its authors. A GitHub PR does not update the account plugin or prove host activation.
