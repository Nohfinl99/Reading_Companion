# CiteGuard integration / Tích hợp CiteGuard

[Bản đồ tài liệu / Documentation map](../README.md) · [Artifact index](../../ARTIFACTS.md)

Vietnamese-first project pack based on SID V5. The 0.3.7 source in PR #11 includes continuity/gate/package corrections; installed-host validation and learning gain remain separate evidence. At the 2026-10-29 review, `main` still described 0.3.5.

Gói này đưa kiến thức có nguồn vào tác vụ đọc qua sáu phase RTC-COE, rồi kiểm lại artifact sau áp dụng. Runtime được định nghĩa trong [CE01–CE06](../../skills/sid-reading-companion/references/citation-evidence.md); tài liệu ở đây giải thích dự án, không tạo instruction song song.

## Đi theo mục tiêu / Choose a route

| Tôi muốn / Goal | Đọc / Read |
|---|---|
| Dùng plugin và biết đầu ra nên nhận | [Usage VI](../usage.vi.md), [EN](../usage.en.md), [artifact VI](../artifacts.vi.md), [EN](../artifacts.en.md), [ví dụ đầu ra](../examples/outputs.md) |
| Hiểu bài toán, phạm vi, người dùng | [Framing brief và scope](framing.md) |
| Xem cách phân IA và tìm đúng tài liệu | [IA pack](information-architecture.md) |
| Copy prompt từng phase và gate sau áp dụng | [Prompt Stack RTC-COE](../../skills/sid-reading-companion/references/citation-evidence.md) |
| Kiểm nguồn phương pháp thiết kế SID V5 | [Mapping và provenance](sid-v5-mapping.md) |
| Đọc Knowledge Package | [Tri thức CiteGuard](../../skills/sid-reading-companion/references/knowledge/citeguard.md) |
| Xem ví dụ áp dụng vào reading và tự kiểm | [Walkthrough và bằng chứng](../../evaluation/citeguard/README.md) |
| Xem prototype, sửa lỗi và release checklist | [Revision notes](revision-notes.md) |
| Kiểm sửa lỗi 0.3.7 và bằng chứng mới | [Correction record](correction-plan.md), [capture/review](../../evaluation/citeguard/sync-0.3.7/README.md), [release checks](../../evaluation/citeguard/sync-0.3.7/release-checks.json) |
| Xem lịch sử roadmap và ba lượt Luna 0.3.6 | [Roadmap lịch sử](roadmap.md), [R3 theo behavioral rubric cũ](../../evaluation/citeguard/luna-rerun-2026-10-29-r3/README.md) |
| Bảo trì, kiểm và đóng gói source | [Quality VI](../quality.vi.md), [EN](../quality.en.md), [allowlist](../../packaging/runtime-files.json), [contributing](../../CONTRIBUTING.md) |

## Quick start

```text
Mode extract. Đối chiếu claim bên dưới với phần tài liệu tôi cung cấp.
Áp dụng CE01–CE06, giữ ngữ cảnh và điều kiện; kết thúc bằng GateRecord
G-CITATION-REVIEW cho artifact. Không đánh đồng nguồn liên quan với hỗ trợ.
Claim: [mệnh đề cần kiểm]
Nguồn/phạm vi: [file hoặc đoạn được phép đọc]
```

The stack uses tools already available on the host. It adds no search service, account memory, external API connection, or automatic checkpoint migration. `G-CITATION-REVIEW` is a specialized R14 gate using SC05. Public examples include synthetic fixtures, assistant-authored reviews and captured delegated-model outputs with their own evidence limits. These are separate from installed-plugin activation and actual learner outcomes.

## Publication boundary

Public source includes paraphrased knowledge, design, synthetic fixtures, validators and test evidence. Private course files, the pasted proposal, PDF binaries, credentials and personal reading sessions are excluded. Preserve the existing MIT license for this project's code; external research remains credited to its authors. A GitHub PR does not update the account plugin or prove host activation.
